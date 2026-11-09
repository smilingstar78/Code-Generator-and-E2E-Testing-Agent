import React, { useState } from 'react';
import axios from 'axios';
import Editor, { DiffEditor } from '@monaco-editor/react';
import { Octokit } from '@octokit/rest';
import { 
  Zap, 
  Terminal, 
  Code2, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  Play, 
  Download, 
  RotateCw, 
  Folder, 
  FileText, 
  GitCompare, 
  GitBranch,
  X
} from 'lucide-react';

const GithubIcon = ({ className = "w-4 h-4" }) => (
  <svg 
    className={className} 
    fill="currentColor" 
    viewBox="0 0 24 24"
  >
    <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
  </svg>
);

export default function App() {
  const [specification, setSpecification] = useState(
    "Create a Python string utility module for reversing words and checking palindromes. Include exhaustive Pytest unit tests."
  );
  const [loading, setLoading] = useState(false);
  const [reTesting, setReTesting] = useState(false);
  const [downloading, setDownloading] = useState(false);
  
  // Workspace and history state
  const [originalFiles, setOriginalFiles] = useState({});
  const [files, setFiles] = useState({});
  const [result, setResult] = useState(null);
  
  // Tabs & active selection
  const [activeTab, setActiveTab] = useState('code'); // 'code' | 'diff' | 'logs'
  const [selectedFile, setSelectedFile] = useState('');

  // GitHub Modal state
  const [showGithubModal, setShowGithubModal] = useState(false);
  const [githubToken, setGithubToken] = useState('');
  const [repoName, setRepoName] = useState('generated-ai-agent-module');
  const [isPrivate, setIsPrivate] = useState(false);
  const [exportingGithub, setExportingGithub] = useState(false);

  const handleExecute = async () => {
    if (!specification.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post('http://127.0.0.1:8000/generate', {
        specification: specification
      });
      setResult(response.data);
      const generatedFiles = response.data.files || {};
      setFiles(generatedFiles);
      setOriginalFiles(JSON.parse(JSON.stringify(generatedFiles)));
      
      if (Object.keys(generatedFiles).length > 0) {
        setSelectedFile(Object.keys(generatedFiles)[0]);
      }
    } catch (error) {
      console.error("Agent API error:", error);
      const detail = error.response?.data?.detail || error.message;
      alert(`Backend Execution Error: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCodeChange = (newContent) => {
    if (!selectedFile) return;
    setFiles((prevFiles) => ({
      ...prevFiles,
      [selectedFile]: newContent || ''
    }));
  };

  const handleReRunTests = async () => {
    if (Object.keys(files).length === 0) return;
    setReTesting(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/run-tests', {
        files: files
      });
      setResult((prev) => ({
        ...prev,
        execution_exit_code: response.data.execution_exit_code,
        test_logs: response.data.test_logs
      }));
    } catch (error) {
      alert("Failed to re-run Docker tests.");
    } finally {
      setReTesting(false);
    }
  };

  const handleDownloadZip = async () => {
    if (Object.keys(files).length === 0) return;
    setDownloading(true);

    try {
      const response = await axios.post(
        'http://127.0.0.1:8000/download-zip',
        { files: files },
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'generated_agent_code.zip');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert("Failed to download ZIP file.");
    } finally {
      setDownloading(false);
    }
  };

  const handleExportToGithub = async (e) => {
    e.preventDefault();
    if (!githubToken || !repoName) {
      alert("Please enter a valid GitHub Personal Access Token and Repository Name.");
      return;
    }
    setExportingGithub(true);

    try {
      const octokit = new Octokit({ auth: githubToken });

      const repoRes = await octokit.rest.repos.createForAuthenticatedUser({
        name: repoName,
        private: isPrivate,
        auto_init: true,
        description: "Generated by Autonomous Code Generation & E2E Testing Agent"
      });

      const owner = repoRes.data.owner.login;
      const repo = repoRes.data.name;

      for (const [filename, content] of Object.entries(files)) {
        await octokit.rest.repos.createOrUpdateFileContents({
          owner,
          repo,
          path: filename,
          message: `Add ${filename} via Agent IDE`,
          content: btoa(unescape(encodeURIComponent(content))),
        });
      }

      alert(`Successfully published repository to GitHub!\n\nURL: ${repoRes.data.html_url}`);
      setShowGithubModal(false);
    } catch (error) {
      console.error("GitHub API export error:", error);
      alert(`GitHub Push Failed: ${error.message}`);
    } finally {
      setExportingGithub(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-mono flex flex-col p-6">
      {/* Header */}
      <header className="border-b border-slate-800 pb-4 mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-amber-500/10 border border-amber-500/30 rounded-lg text-amber-500">
            <Zap className="w-6 h-6 fill-amber-500/20" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
              Autonomous Cloud IDE & Agent Sandbox
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Warm Docker Sandbox • Monaco Diff Inspector • GitHub Integration
            </p>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
        
        {/* Left Specification Form */}
        <section className="lg:col-span-4 flex flex-col gap-4">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
              System Specification Prompt
            </label>

            <textarea
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-amber-500 resize-none font-sans"
              rows={10}
              value={specification}
              onChange={(e) => setSpecification(e.target.value)}
              placeholder="Describe the functionality or module to generate..."
            />

            <button
              onClick={handleExecute}
              disabled={loading}
              className="mt-4 w-full bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-slate-950 font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50 cursor-pointer shadow-lg shadow-amber-500/10"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-slate-950" />
                  Running Agent Graph...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-slate-950" />
                  Execute Agent Pipeline
                </>
              )}
            </button>
          </div>
        </section>

        {/* Right Cloud IDE Column */}
        <section className="lg:col-span-8 flex flex-col gap-4">
          
          {/* Execution Status & Action Controls */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-400 uppercase font-semibold">Status:</span>
              {loading ? (
                <span className="text-xs text-amber-400 font-bold flex items-center gap-1.5">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  Running Multi-Agent Pipeline...
                </span>
              ) : result ? (
                result.execution_exit_code === 0 ? (
                  <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-md">
                    <CheckCircle2 className="w-4 h-4" /> PASSED (Exit Code 0)
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 text-xs font-bold text-red-400 bg-red-500/10 border border-red-500/20 px-3 py-1 rounded-md">
                    <XCircle className="w-4 h-4" /> FAILED (Exit Code {result.execution_exit_code})
                  </span>
                )
              ) : (
                <span className="text-xs text-slate-500">Awaiting execution request</span>
              )}
            </div>

            {/* Action Buttons */}
            {Object.keys(files).length > 0 && (
              <div className="flex items-center gap-2">
                <button
                  onClick={handleReRunTests}
                  disabled={reTesting}
                  className="bg-slate-800 hover:bg-slate-700 text-xs font-semibold px-3 py-1.5 rounded border border-slate-700 text-slate-200 flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  <RotateCw className={`w-3.5 h-3.5 ${reTesting ? 'animate-spin' : ''}`} />
                  Fast Docker Re-Test
                </button>
                <button
                  onClick={handleDownloadZip}
                  disabled={downloading}
                  className="bg-emerald-600/20 hover:bg-emerald-600/30 text-xs font-semibold px-3 py-1.5 rounded border border-emerald-500/30 text-emerald-300 flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  <Download className="w-3.5 h-3.5" />
                  Export ZIP
                </button>
                <button
                  onClick={() => setShowGithubModal(true)}
                  className="bg-purple-600/20 hover:bg-purple-600/30 text-xs font-semibold px-3 py-1.5 rounded border border-purple-500/30 text-purple-300 flex items-center gap-1.5 cursor-pointer"
                >
                  <GithubIcon className="w-3.5 h-3.5" />
                  Push to GitHub
                </button>
              </div>
            )}
          </div>

          {/* IDE Inspector Container */}
          <div className="flex-1 bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden flex flex-col min-h-[500px]">
            {/* View Tabs */}
            <div className="flex items-center border-b border-slate-800 bg-slate-950/40 px-4 gap-4">
              <button
                onClick={() => setActiveTab('code')}
                className={`py-3 text-xs font-semibold flex items-center gap-1.5 border-b-2 transition-colors cursor-pointer ${
                  activeTab === 'code' ? 'border-amber-500 text-amber-400' : 'border-transparent text-slate-400'
                }`}
              >
                <Code2 className="w-4 h-4" /> Code Editor
              </button>
              <button
                onClick={() => setActiveTab('diff')}
                className={`py-3 text-xs font-semibold flex items-center gap-1.5 border-b-2 transition-colors cursor-pointer ${
                  activeTab === 'diff' ? 'border-amber-500 text-amber-400' : 'border-transparent text-slate-400'
                }`}
              >
                <GitCompare className="w-4 h-4" /> Monaco Diff Viewer
              </button>
              <button
                onClick={() => setActiveTab('logs')}
                className={`py-3 text-xs font-semibold flex items-center gap-1.5 border-b-2 transition-colors cursor-pointer ${
                  activeTab === 'logs' ? 'border-amber-500 text-amber-400' : 'border-transparent text-slate-400'
                }`}
              >
                <Terminal className="w-4 h-4" /> Docker Pytest Logs
              </button>
            </div>

            {/* Split Workspace Layout */}
            <div className="flex-1 flex overflow-hidden">
              
              {/* File Tree Sidebar */}
              <aside className="w-56 bg-slate-950/80 border-r border-slate-800 p-3 flex flex-col gap-1 overflow-y-auto">
                <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5 px-2 py-1">
                  <Folder className="w-3.5 h-3.5 text-amber-500" /> Workspace Files
                </div>
                
                {Object.keys(files).length > 0 ? (
                  Object.keys(files).map((filename) => (
                    <button
                      key={filename}
                      onClick={() => setSelectedFile(filename)}
                      className={`w-full text-left text-xs px-2.5 py-2 rounded flex items-center gap-2 transition-colors cursor-pointer ${
                        selectedFile === filename
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30 font-medium'
                          : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                      }`}
                    >
                      <FileText className="w-3.5 h-3.5 shrink-0 text-slate-400" />
                      <span className="truncate">{filename}</span>
                    </button>
                  ))
                ) : (
                  <div className="text-[11px] text-slate-600 italic px-2 py-4">
                    No generated files.
                  </div>
                )}
              </aside>

              {/* Editor Surface */}
              <div className="flex-1 bg-slate-950 relative overflow-hidden">
                {activeTab === 'code' ? (
                  Object.keys(files).length > 0 && selectedFile ? (
                    <Editor
                      height="100%"
                      defaultLanguage="python"
                      theme="vs-dark"
                      value={files[selectedFile]}
                      onChange={handleCodeChange}
                      options={{
                        fontSize: 13,
                        minimap: { enabled: false },
                        scrollBeyondLastLine: false,
                        automaticLayout: true,
                        tabSize: 4,
                      }}
                    />
                  ) : (
                    <div className="h-full flex items-center justify-center text-slate-500 text-xs">
                      Select a file from the tree sidebar.
                    </div>
                  )
                ) : activeTab === 'diff' ? (
                  Object.keys(files).length > 0 && selectedFile ? (
                    <DiffEditor
                      height="100%"
                      language="python"
                      theme="vs-dark"
                      original={originalFiles[selectedFile] || ''}
                      modified={files[selectedFile] || ''}
                      options={{
                        fontSize: 13,
                        minimap: { enabled: false },
                        renderSideBySide: true,
                        automaticLayout: true,
                        readOnly: false
                      }}
                    />
                  ) : (
                    <div className="h-full flex items-center justify-center text-slate-500 text-xs">
                      Select a file to compare changes.
                    </div>
                  )
                ) : (
                  result?.test_logs ? (
                    <pre className="p-4 text-slate-300 leading-relaxed whitespace-pre-wrap font-mono text-xs overflow-auto h-full">
                      <code>{result.test_logs}</code>
                    </pre>
                  ) : (
                    <div className="h-full flex items-center justify-center text-slate-500 text-xs">
                      No Docker logs available.
                    </div>
                  )
                )}
              </div>

            </div>

          </div>

        </section>
      </main>

      {/* GitHub Export Modal */}
      {showGithubModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <GithubIcon className="w-4 h-4 text-purple-400" /> Push Codebase to GitHub
              </h3>
              <button
                onClick={() => setShowGithubModal(false)}
                className="text-slate-400 hover:text-slate-200 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleExportToGithub} className="flex flex-col gap-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 font-semibold">GitHub Personal Access Token (PAT)</label>
                <input
                  type="password"
                  required
                  value={githubToken}
                  onChange={(e) => setGithubToken(e.target.value)}
                  placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2.5 text-slate-200 focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-semibold">Repository Name</label>
                <input
                  type="text"
                  required
                  value={repoName}
                  onChange={(e) => setRepoName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2.5 text-slate-200 focus:outline-none focus:border-purple-500"
                />
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="private-repo"
                  checked={isPrivate}
                  onChange={(e) => setIsPrivate(e.target.checked)}
                  className="rounded bg-slate-950 border-slate-800 text-purple-500 focus:ring-0 cursor-pointer"
                />
                <label htmlFor="private-repo" className="text-slate-300 cursor-pointer">
                  Create as Private Repository
                </label>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowGithubModal(false)}
                  className="px-4 py-2 rounded text-slate-400 hover:text-slate-200 font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={exportingGithub}
                  className="bg-purple-600 hover:bg-purple-500 text-slate-100 font-bold px-4 py-2 rounded flex items-center gap-2 transition-all cursor-pointer disabled:opacity-50"
                >
                  {exportingGithub ? "Pushing Files..." : "Create & Push"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}