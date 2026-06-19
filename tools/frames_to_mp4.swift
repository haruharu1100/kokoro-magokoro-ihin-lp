import AVFoundation
import AppKit
import Foundation

let args = CommandLine.arguments
guard args.count >= 5 else {
    fputs("usage: frames_to_mp4.swift <framesDir> <output.mp4> <fps> <frameCount> [width] [height]\n", stderr)
    exit(2)
}

let framesDir = URL(fileURLWithPath: args[1], isDirectory: true)
let outputURL = URL(fileURLWithPath: args[2])
let fps = Int32(args[3]) ?? 30
let frameCount = Int(args[4]) ?? 300
let width = args.count >= 6 ? (Int(args[5]) ?? 720) : 720
let height = args.count >= 7 ? (Int(args[6]) ?? 1280) : 1280

try? FileManager.default.removeItem(at: outputURL)

let writer = try AVAssetWriter(outputURL: outputURL, fileType: .mp4)
let settings: [String: Any] = [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width,
    AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [
        AVVideoAverageBitRateKey: 5_000_000,
        AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel
    ]
]

let input = AVAssetWriterInput(mediaType: .video, outputSettings: settings)
input.expectsMediaDataInRealTime = false

let attrs: [String: Any] = [
    kCVPixelBufferPixelFormatTypeKey as String: Int(kCVPixelFormatType_32BGRA),
    kCVPixelBufferWidthKey as String: width,
    kCVPixelBufferHeightKey as String: height
]
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: attrs)

guard writer.canAdd(input) else {
    fputs("cannot add writer input\n", stderr)
    exit(3)
}
writer.add(input)

guard writer.startWriting() else {
    fputs("failed to start writing: \(writer.error?.localizedDescription ?? "unknown")\n", stderr)
    exit(4)
}
writer.startSession(atSourceTime: .zero)

func pixelBuffer(from image: NSImage) -> CVPixelBuffer? {
    guard let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else { return nil }
    var buffer: CVPixelBuffer?
    let status = CVPixelBufferCreate(kCFAllocatorDefault, width, height, kCVPixelFormatType_32BGRA, nil, &buffer)
    guard status == kCVReturnSuccess, let px = buffer else { return nil }
    CVPixelBufferLockBaseAddress(px, [])
    defer { CVPixelBufferUnlockBaseAddress(px, []) }
    guard let context = CGContext(
        data: CVPixelBufferGetBaseAddress(px),
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: CVPixelBufferGetBytesPerRow(px),
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.premultipliedFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue
    ) else { return nil }
    context.draw(cg, in: CGRect(x: 0, y: 0, width: width, height: height))
    return px
}

let frameDuration = CMTime(value: 1, timescale: fps)
var frame = 0

while frame < frameCount {
    if input.isReadyForMoreMediaData {
        let url = framesDir.appendingPathComponent(String(format: "frame_%04d.png", frame))
        guard let img = NSImage(contentsOf: url), let px = pixelBuffer(from: img) else {
            fputs("failed to load frame \(frame)\n", stderr)
            exit(5)
        }
        let time = CMTimeMultiply(frameDuration, multiplier: Int32(frame))
        if !adaptor.append(px, withPresentationTime: time) {
            fputs("failed to append frame \(frame): \(writer.error?.localizedDescription ?? "unknown")\n", stderr)
            exit(6)
        }
        frame += 1
    } else {
        Thread.sleep(forTimeInterval: 0.01)
    }
}

input.markAsFinished()
let semaphore = DispatchSemaphore(value: 0)
writer.finishWriting {
    semaphore.signal()
}
semaphore.wait()

if writer.status == .completed {
    print(outputURL.path)
} else {
    fputs("writer failed: \(writer.error?.localizedDescription ?? "unknown")\n", stderr)
    exit(7)
}
