import React from 'react';
import { Eye, ExternalLink } from 'lucide-react';

export default function WebPreview({ files }) {
  // Check for HTML or JavaScript entrypoints
  const htmlFile = files['index.html'] || files['index.htm'];
  const jsFile = files['script.js'] || files['app.js'];
  const cssFile = files['style.css'] || files['styles.css'];

  // Construct combined HTML srcDoc string for instant rendering
  const srcDoc = htmlFile
    ? htmlFile.replace('</head>', `<style>${cssFile || ''}</style></head>`)
              .replace('</body>', `<script>${jsFile || ''}</script></body>`)
    : `
      <!DOCTYPE html>
      <html>
        <head>
          <style>
            body { background: #020617; color: #f8fafc; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            ${cssFile || ''}
          </style>
        </head>
        <body>
          <div id="root"></div>
          <script>${jsFile || ''}</script>
        </body>
      </html>
    `;

  return (
    <div className="h-full flex flex-col bg-slate-950">
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-2 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2 text-slate-400">
          <Eye className="w-4 h-4 text-amber-500" />
          <span className="font-semibold text-slate-200">Live Browser Preview</span>
        </div>
        <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">
          Active Sandbox View
        </span>
      </div>
      <iframe
        title="Web Preview"
        srcDoc={srcDoc}
        className="w-full flex-1 border-none bg-white"
        sandbox="allow-scripts allow-modals allow-same-origin"
      />
    </div>
  );
}