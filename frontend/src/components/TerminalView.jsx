import React, { useEffect, useRef } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';

export default function TerminalView() {
  const terminalRef = useRef(null);

  useEffect(() => {
    const term = new Terminal({
      cursorBlink: true,
      theme: {
        background: '#020617',
        foreground: '#f8fafc',
        cursor: '#f59e0b',
        selectionBackground: '#334155',
      },
      fontSize: 13,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
    });

    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.open(terminalRef.current);
    fitAddon.fit();

    // Connect to FastAPI WebSocket terminal endpoint
    const ws = new WebSocket('ws://127.0.0.1:8000/ws/terminal');

    ws.onopen = () => {
      term.write('\r\n\x1b[32m🚀 Interactive Sandbox Terminal Connected!\x1b[0m\r\n\r\n');
    };

    ws.onmessage = (event) => {
      term.write(event.data);
    };

    term.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(data);
      }
    });

    const handleResize = () => fitAddon.fit();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      ws.close();
      term.dispose();
    };
  }, []);

  return (
    <div className="h-full w-full bg-slate-950 p-2 overflow-hidden flex flex-col">
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-2 flex items-center justify-between text-xs font-mono">
        <span className="text-slate-300 font-bold">Interactive Container Shell (/app)</span>
        <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">
          Docker PTY Connected
        </span>
      </div>
      <div ref={terminalRef} className="flex-1 w-full overflow-hidden" />
    </div>
  );
}