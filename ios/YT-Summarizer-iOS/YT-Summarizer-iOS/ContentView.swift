//
//  ContentView.swift
//  YT-Summarizer-iOS
//
//  Created by Sharan Thakur on 09/01/25.
//

import SwiftUI

struct ContentView: View {
    @State private var ytLink = ""
    @State private var progressState = ProgressState.idle
    @FocusState private var isFocused: Bool
    
    @State private var task: Task<Void, Error>? = nil
    
    enum ProgressState {
        case idle
        case loading
        case done(Result<String, SummarizerError>)
    }
    
    var body: some View {
        Form {
            Section("Input") {
                TextField("Enter YouTube Link", text: $ytLink, prompt: Text("Enter YouTube Link"), axis: .vertical)
                    .focused($isFocused)
                    .submitLabel(.done)
                    .onSubmit {
                        isFocused = false
                    }
                
                Button("Summarize", action: makeRequest)
                    .disabled(disableButton)
                
                if let task {
                    Button("Cancel task", role: .cancel) {
                        task.cancel()
                        self.task = nil
                    }
                }
            }
            
            Section("Video") {
                if let ytURL {
                    EmbedYTVideoView(ytURL)
                        .frame(height: 100)
                        .frame(maxWidth: .infinity, alignment: .center)
                    
                    Link("Open in YouTube", destination: ytURL)
                }
            }
            
            Section("Result") {
                // SummaryText
                switch progressState {
                case .idle:
                    EmptyView()
                case .loading:
                    ProgressView()
                case .done(let result):
                    switch result {
                    case .success(let summary):
                        if task != nil {
                            Text("Generating...")
                        }
                        Text(LocalizedStringKey(summary))
                            .padding()
                            .contextMenu {
                                let items = [summary, ytURL?.absoluteString].compactMap { $0 }
                                ShareLink(items: items, subject: Text("Summary of \(ytURL?.absoluteString ?? "")")) {
                                    Label("Share", systemImage: "square.and.arrow.up")
                                }
                                .labelStyle(.titleAndIcon)
                            }
                    case .failure(let error):
                        Text(error.error)
                            .padding()
                            .foregroundColor(.red)
                    }
                }
            }
        }
        .alert(isPresented: isPresentingError, error: error) { }
    }
}

extension ContentView {
    var ytURL: URL? {
        URL(string: ytLink)
    }
    
    var error: SummarizerError? {
        if case .done(.failure(let error)) = progressState {
            return error
        } else {
            return nil
        }
    }
    
    var isPresentingError: Binding<Bool> {
        Binding {
            if case .done(.failure) = progressState {
                return true
            } else {
                return false
            }
        } set: { _ in
            progressState = .idle
        }
    }
    
    var disableButton: Bool {
        if case .loading = progressState {
            return true
        } else {
            return ytLink.isEmpty || URL(string: ytLink) == nil
        }
    }
}

extension ContentView {
    func makeRequest() {
        isFocused = false
        guard let ytURL = ytURL else { return }
        guard let myURL = URL(string: "http://192.168.1.127:8000/summarize") else { return }
        progressState = .loading
        task = Task {
            var request = URLRequest(url: myURL)
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpMethod = "POST"
            request.httpBody = try JSONEncoder().encode(YTRequest(link: ytURL.absoluteString))
            let session = URLSession.shared
            
            try Task.checkCancellation()
            
            let (stream, response) = try await session.bytes(for: request)
            
            try Task.checkCancellation()
            
            if let httpResponse = response as? HTTPURLResponse {
                print(httpResponse.statusCode)
            }
            
            var summary = ""
            for try await line in stream.lines {
                try Task.checkCancellation()
                summary += line
                progressState = .done(.success(summary))
            }
        }
        
        Task {
            do {
                try await task?.value
                task?.cancel()
                task = nil
            } catch is CancellationError {
                print(":cancelled")
            } catch {
                task?.cancel()
                task = nil
                print(error)
                let e = SummarizerError(error: error.localizedDescription)
                progressState = .done(.failure(e))
            }
        }
    }
}

struct YTRequest: Encodable {
    let link: String
}

struct SummarizerError: LocalizedError, CustomStringConvertible {
    let error: String
    
    var description: String { error }
    var errorDescription: String? { error }
}

#Preview {
    ContentView()
}
