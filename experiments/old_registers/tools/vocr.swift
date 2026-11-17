// Apple Vision OCR: prints "x y w h<TAB>text" per recognized line (normalized coords, origin bottom-left).
import Foundation
import Vision
import AppKit
let path = CommandLine.arguments[1]
guard let img = NSImage(contentsOfFile: path), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.usesLanguageCorrection = false
if CommandLine.arguments.count > 2 { req.revision = Int(CommandLine.arguments[2])! }
try VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
for o in req.results ?? [] {
  guard let t = o.topCandidates(1).first else { continue }
  let b = o.boundingBox
  print(String(format: "%.4f %.4f %.4f %.4f\t", b.minX, b.minY, b.width, b.height) + t.string)
}
