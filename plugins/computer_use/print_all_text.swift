import Cocoa
import Vision

let args = CommandLine.arguments
let imagePath = args[1]
guard let img = NSImage(contentsOfFile: imagePath),
      let cgImage = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }

let requestHandler = VNImageRequestHandler(cgImage: cgImage, options: [:])
let request = VNRecognizeTextRequest { (request, error) in
    guard let observations = request.results as? [VNRecognizedTextObservation] else { return }
    for observation in observations {
        if let topCandidate = observation.topCandidates(1).first {
            print(topCandidate.string)
        }
    }
}
if #available(macOS 11.0, *) {
    request.recognitionLanguages = ["zh-Hans", "zh-Hant", "en-US"]
}
try? requestHandler.perform([request])
