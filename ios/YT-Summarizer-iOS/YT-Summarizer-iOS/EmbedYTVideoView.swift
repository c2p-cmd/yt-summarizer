//
//  EmbedYTVideo.swift
//  YT-Summarizer-iOS
//
//  Created by Sharan Thakur on 09/01/25.
//

import SwiftUI
import WebKit

struct EmbedYTVideoView: UIViewRepresentable {
    let ytURL: URL
    
    init(_ ytURL: URL) {
        self.ytURL = ytURL
    }
    
    func makeUIView(context: Context) -> WKWebView {
        let uiView = WKWebView()
        let html: String
        
        // make sure url is from youtube
        let host = ytURL.host
        if host?.contains("youtube.com") == true || host?.contains("youtu.be") == true {
            print("Invalid URL")
        }
        
        if let embedURL = URL(string: ytURL.absoluteString.replacingOccurrences(of: "watch?v=", with: "embed/")) {
            html = EmbedYTVideoView.html(for: embedURL)
        } else {
            print("Invalid URL")
            html = EmbedYTVideoView.html(for: ytURL)
        }
        uiView.loadHTMLString(html, baseURL: nil)
        
        return uiView
    }
    
    func updateUIView(_ uiView: WKWebView, context: Context) {
        guard let embedURL = URL(string: ytURL.absoluteString.replacingOccurrences(of: "watch?v=", with: "embed/")) else { return }
        guard uiView.url != embedURL else { return }
        
        let html = EmbedYTVideoView.html(for: embedURL)
        uiView.loadHTMLString(html, baseURL: nil)
    }
    
    static func html(for url: URL) -> String {
"""
    <iframe width="600" height="600" src="\(url.absoluteString)">
    </iframe> 
"""
    }
}

