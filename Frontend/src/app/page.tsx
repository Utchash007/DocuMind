"use client";

import { useState, useEffect, useRef } from "react";

// API Base URL pointing to the FastAPI Backend
const API_BASE = "http://localhost:8000";

interface Message {
  id: string;
  sender: "user" | "ai";
  text: string;
  citations?: { sentence: string; page: number }[];
}

export default function Home() {
  // Application State
  const [files, setFiles] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [chatHistory, setChatHistory] = useState<Message[]>([
    {
      id: "welcome",
      sender: "ai",
      text: "Hello! I am DocuMind, your AI document assistant. Upload a PDF on the left and ask me questions about it!",
    },
  ]);
  const [query, setQuery] = useState("");
  const [uploading, setUploading] = useState(false);
  const [querying, setQuerying] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll chat to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, querying]);

  // Fetch list of processed files on mount
  const fetchFiles = async () => {
    try {
      const res = await fetch(`${API_BASE}/files`);
      if (res.ok) {
        const data = await res.json();
        setFiles(data.files || []);
      }
    } catch (err) {
      console.error("Failed to fetch files:", err);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  // Handle PDF file upload
  const handleUpload = async (file: File) => {
    if (!file.name.endsWith(".pdf")) {
      setErrorMsg("Only PDF files are supported!");
      return;
    }

    setUploading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (res.ok) {
        setSuccessMsg(`Successfully processed '${file.name}'`);
        setSelectedFile(file.name);
        fetchFiles();
      } else {
        setErrorMsg(data.detail || "File processing failed.");
      }
    } catch (err) {
      setErrorMsg("Failed to connect to backend server.");
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  // Drag and drop event handlers
  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const onDragLeave = () => {
    setDragOver(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleUpload(file);
    }
  };

  // Trigger file dialog
  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const onFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleUpload(file);
    }
  };

  // Handle Message Submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      sender: "user",
      text: query,
    };

    setChatHistory((prev) => [...prev, userMessage]);
    setQuery("");
    setQuerying(true);
    setErrorMsg(null);

    const bodyFormData = new FormData();
    bodyFormData.append("query", userMessage.text);
    if (selectedFile) {
      bodyFormData.append("filename", selectedFile);
    }

    try {
      const res = await fetch(`${API_BASE}/query`, {
        method: "POST",
        body: bodyFormData,
      });

      const data = await res.json();
      if (res.ok) {
        setChatHistory((prev) => [
          ...prev,
          {
            id: `msg-${Date.now()}-ai`,
            sender: "ai",
            text: data.answer,
            citations: data.citations || [],
          },
        ]);
      } else {
        setErrorMsg(data.detail || "Failed to generate answer.");
      }
    } catch (err) {
      setErrorMsg("Connection to backend server lost.");
      console.error(err);
    } finally {
      setQuerying(false);
    }
  };

  return (
    <div className="flex h-screen w-screen bg-slate-950 font-sans text-slate-100 overflow-hidden">
      {/* LEFT PANEL: Document uploads & list */}
      <aside className="w-80 border-r border-slate-800 bg-slate-900/60 backdrop-blur-md flex flex-col p-6 gap-6">
        <div>
          <h2 className="text-xl font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent flex items-center gap-2">
            <svg className="w-6 h-6 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            DocuMind
          </h2>
          <p className="text-xs text-slate-400 mt-1">AI-Powered Hybrid RAG System</p>
        </div>

        {/* Upload Box */}
        <div
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={triggerFileInput}
          className={`flex-shrink-0 cursor-pointer border-2 border-dashed rounded-xl p-4 flex flex-col items-center justify-center gap-2 text-center transition-all ${
            dragOver
              ? "border-violet-500 bg-violet-950/20"
              : "border-slate-800 hover:border-slate-700 bg-slate-950/40"
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={onFileSelect}
            className="hidden"
            accept=".pdf"
          />
          {uploading ? (
            <div className="flex flex-col items-center gap-2">
              <div className="w-8 h-8 rounded-full border-2 border-violet-500/20 border-t-violet-500 animate-spin" />
              <span className="text-xs text-violet-400 font-medium">Ingesting PDF...</span>
            </div>
          ) : (
            <>
              <svg className="w-8 h-8 text-slate-400 group-hover:text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <div>
                <span className="text-sm font-semibold text-slate-200 block">Upload PDF</span>
                <span className="text-xs text-slate-500">Drag & drop or browse</span>
              </div>
            </>
          )}
        </div>

        {/* File Selection Filter */}
        <div className="flex-1 flex flex-col min-h-0 gap-3">
          <div className="text-xs font-semibold text-slate-500 tracking-wider uppercase">Active Context</div>
          <div className="flex-1 overflow-y-auto pr-1 flex flex-col gap-2">
            <button
              onClick={() => setSelectedFile(null)}
              className={`w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center justify-between border ${
                selectedFile === null
                  ? "bg-violet-950/30 border-violet-500/30 text-violet-300"
                  : "bg-slate-950/30 border-transparent hover:bg-slate-800/40 text-slate-400"
              }`}
            >
              <span className="truncate">All Documents</span>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </button>

            {files.map((file) => (
              <button
                key={file}
                onClick={() => setSelectedFile(file)}
                className={`w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center justify-between border ${
                  selectedFile === file
                    ? "bg-violet-950/30 border-violet-500/30 text-violet-300"
                    : "bg-slate-950/30 border-transparent hover:bg-slate-800/40 text-slate-400"
                }`}
              >
                <span className="truncate text-left mr-2 flex-1">{file}</span>
                <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </button>
            ))}

            {files.length === 0 && (
              <div className="text-center py-8 text-slate-600 text-xs italic">
                No documents uploaded yet.
              </div>
            )}
          </div>
        </div>

        {/* Message alerts */}
        {errorMsg && (
          <div className="bg-red-950/30 border border-red-500/30 rounded-lg p-3 text-xs text-red-400 flex items-start gap-2">
            <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{errorMsg}</span>
          </div>
        )}
        {successMsg && (
          <div className="bg-emerald-950/30 border border-emerald-500/30 rounded-lg p-3 text-xs text-emerald-400 flex items-start gap-2">
            <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{successMsg}</span>
          </div>
        )}
      </aside>

      {/* RIGHT PANEL: Chat Area */}
      <main className="flex-1 flex flex-col bg-slate-950 relative">
        {/* Header bar */}
        <header className="h-16 border-b border-slate-800 bg-slate-900/30 backdrop-blur-md flex items-center px-8 justify-between">
          <div className="flex items-center gap-3">
            <span className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse" />
            <h1 className="text-sm font-semibold text-slate-200">
              Query Workspace: <span className="text-violet-400">{selectedFile ? selectedFile : "All Documents"}</span>
            </h1>
          </div>
        </header>

        {/* Messages Stream */}
        <section className="flex-1 overflow-y-auto px-16 py-8 flex flex-col gap-6">
          {chatHistory.map((msg) => (
            <div
              key={msg.id}
              className={`flex w-full max-w-3xl ${
                msg.sender === "user" ? "justify-end ml-auto" : "justify-start"
              }`}
            >
              <div
                className={`rounded-2xl px-5 py-3.5 leading-relaxed text-sm ${
                  msg.sender === "user"
                    ? "bg-violet-600 text-slate-50 rounded-br-none"
                    : "bg-slate-900 border border-slate-800 text-slate-100 rounded-bl-none shadow-xl"
                }`}
              >
                {/* Message text */}
                <div className="whitespace-pre-line">{msg.text}</div>

                {/* Citations panel for AI answers */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800/80">
                    <div className="text-xs font-semibold text-violet-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Page Citations
                    </div>
                    <ol className="flex flex-col gap-2">
                      {msg.citations.map((cit, idx) => (
                        <li
                          key={idx}
                          className="bg-slate-950/60 rounded-lg p-2.5 border border-slate-800/40 text-xs leading-normal text-slate-300 hover:bg-slate-950/90 transition-all"
                        >
                          <span className="font-semibold text-violet-300 block mb-0.5">Page {cit.page}:</span>
                          <span className="italic font-light">"{cit.sentence}"</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Loader when generating answer */}
          {querying && (
            <div className="flex w-full max-w-3xl justify-start">
              <div className="bg-slate-900 border border-slate-800 rounded-2xl rounded-bl-none px-6 py-4 shadow-xl flex items-center gap-3">
                <div className="flex gap-1.5 items-center">
                  <span className="w-2 h-2 bg-violet-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <span className="w-2 h-2 bg-violet-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <span className="w-2 h-2 bg-violet-400 rounded-full animate-bounce" />
                </div>
                <span className="text-xs text-slate-400 font-medium">Consulting context...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </section>

        {/* Query Input Box */}
        <footer className="p-8 bg-slate-950">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative flex items-center">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={querying || files.length === 0}
              placeholder={
                files.length === 0
                  ? "Please upload a document to begin..."
                  : `Ask a question about ${selectedFile ? selectedFile : "any document"}...`
              }
              className="w-full h-14 bg-slate-900 border border-slate-800 rounded-full pl-6 pr-16 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-violet-500 transition-all shadow-2xl disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={querying || !query.trim() || files.length === 0}
              className="absolute right-2.5 w-10 h-10 rounded-full bg-violet-600 hover:bg-violet-500 text-slate-50 flex items-center justify-center transition-all disabled:opacity-50 disabled:bg-slate-800"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
          </form>
        </footer>
      </main>
    </div>
  );
}
