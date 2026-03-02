"use client";

import React, { useState } from "react";
import { 
  Activity, ShieldAlert, CheckCircle, FileText, Bot, FileSearch, 
  Plus, Trash2, Copy, FileCode2, UploadCloud, Server, Database, Share2, Brain 
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

export default function ProposalDashboard() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState("Ready to process...");
  const [result, setResult] = useState<any>(null);
  const [editableDraft, setEditableDraft] = useState("");

  const [companyName, setCompanyName] = useState("Keshav AI Solutions");
  const [capabilities, setCapabilities] = useState("We specialize in aerospace engineering, data analytics, and building robust backend infrastructure for federal agencies.");
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  
  const [pastProjects, setPastProjects] = useState([
    { project_name: "Project Titan - NASA", naics_codes: "541512", standards: "ISO 9001" },
    { project_name: "Project Omega - Pentagon", naics_codes: "541512", standards: "FIPS 201" }
  ]);

  const handleAddProject = () => setPastProjects([...pastProjects, { project_name: "", naics_codes: "", standards: "" }]);
  const handleRemoveProject = (index: number) => setPastProjects(pastProjects.filter((_, i) => i !== index));
  const handleProjectChange = (index: number, field: string, value: string) => {
    const newProjects = [...pastProjects] as any;
    newProjects[index][field] = value;
    setPastProjects(newProjects);
  };

  const startAgentPipeline = async () => {
    if (!pdfFile) {
      alert("Please upload an RFP Document (PDF) first!");
      return;
    }
    setIsGenerating(true);
    setResult(null);
    setEditableDraft("");
    setProgress(5);
    setStatusText("Uploading RFP to secure server...");

    try {
      const formData = new FormData();
      formData.append("file", pdfFile);
      const uploadRes = await fetch("http://127.0.0.1:8000/api/upload-pdf", { method: "POST", body: formData });
      if (!uploadRes.ok) throw new Error("Upload failed");
      const uploadData = await uploadRes.json();
      
      setProgress(15);
      setStatusText("Initializing LangGraph Pipeline...");

      const statuses = [
        "Extracting constraints from PDF via FAISS...",
        "Traversing NetworkX Knowledge Graph...",
        "Agent 1: Drafting initial proposal...",
        "Agent 2: Auditing draft against RFP constraints...",
        "Agent 1: Rewriting based on Auditor feedback...",
        "Finalizing compliance score..."
      ];
      
      let step = 0;
      const interval = setInterval(() => {
        if (step < statuses.length) {
          setStatusText(statuses[step]);
          setProgress((prev) => prev + 12);
          step++;
        }
      }, 4000);

      const response = await fetch("http://127.0.0.1:8000/api/generate-proposal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          opportunity_id: `SAM_${Math.floor(Math.random() * 10000)}`,
          pdf_path: uploadData.file_path, 
          user_profile: {
            company_name: companyName,
            capabilities_statement: capabilities,
            past_performance: pastProjects.map(p => ({
              project_name: p.project_name,
              naics_codes: p.naics_codes.split(',').map(s => s.trim()).filter(Boolean),
              standards: p.standards.split(',').map(s => s.trim()).filter(Boolean)
            }))
          }
        }),
      });

      const data = await response.json();
      clearInterval(interval);
      setProgress(100);
      setStatusText("Pipeline Complete!");
      setResult(data);
      setEditableDraft(data.draft_proposal);
      
    } catch (error) {
      setStatusText("Error in processing.");
      console.error(error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExportWord = () => {
    if (editableDraft) {
      const htmlContent = editableDraft.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
      const header = "<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'><head><meta charset='utf-8'></head><body>";
      const source = 'data:application/vnd.ms-word;charset=utf-8,' + encodeURIComponent(header + htmlContent + "</body></html>");
      const link = document.createElement("a");
      link.href = source;
      link.download = `${companyName.replace(/\s+/g, '_')}_Proposal.doc`;
      link.click();
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col font-sans">
      <div className="flex-grow p-4 md:p-8 max-w-7xl mx-auto w-full space-y-8 flex flex-col">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
              GovPreneurs Agentic AI
            </h1>
            <p className="text-slate-400 mt-1">Proposal Intelligence & Compliance Canvas</p>
          </div>
          <Badge variant="outline" className="w-fit border-cyan-500 text-cyan-400 bg-cyan-500/10 px-4 py-1.5">
            <Activity className="w-4 h-4 mr-2 inline animate-pulse" />
            System Online
          </Badge>
        </div>

        {/* ALIGNMENT FIX: items-stretch forces both columns to be equal height */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch flex-grow">
          
          {/* LEFT COLUMN: Flex layout to push bottom card down */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            
            {/* Form Card */}
            <Card className="bg-slate-900 border-slate-800 shadow-xl shrink-0">
              <CardHeader>
                <CardTitle className="text-slate-200 text-lg flex items-center">
                  <FileSearch className="w-5 h-5 mr-2 text-blue-400" />
                  Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-5">
                <div className="p-4 border-2 border-dashed border-slate-700 rounded-xl bg-slate-950 hover:border-blue-500 transition-all group">
                  <label className="text-xs text-slate-400 uppercase font-bold tracking-widest mb-2 block flex items-center cursor-pointer">
                    <UploadCloud className="w-4 h-4 mr-2 text-blue-400" /> Upload RFP PDF
                  </label>
                  <input type="file" accept=".pdf" onChange={(e) => setPdfFile(e.target.files ? e.target.files[0] : null)} className="w-full text-xs text-slate-300 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer" />
                  {pdfFile && <p className="text-xs text-green-400 mt-2 font-mono">✓ {pdfFile.name}</p>}
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="text-xs text-slate-400 uppercase font-bold tracking-widest mb-1.5 block">Company Name</label>
                    <input type="text" value={companyName} onChange={(e) => setCompanyName(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200 focus:border-blue-500 outline-none" />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 uppercase font-bold tracking-widest mb-1.5 block">Capabilities</label>
                    <textarea value={capabilities} onChange={(e) => setCapabilities(e.target.value)} rows={3} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200 focus:border-blue-500 outline-none resize-none" />
                  </div>
                </div>

                <Separator className="bg-slate-800" />

                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <label className="text-xs text-slate-400 uppercase font-bold tracking-widest">Past Performance</label>
                    <Button variant="ghost" size="sm" onClick={handleAddProject} className="h-7 text-xs text-blue-400 hover:bg-slate-800">
                      <Plus className="w-3 h-3 mr-1" /> Add
                    </Button>
                  </div>
                  <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                    {pastProjects.map((project, index) => (
                      <div key={index} className="p-3 bg-slate-950 border border-slate-800 rounded-lg relative group">
                        <button onClick={() => handleRemoveProject(index)} className="absolute top-2 right-2 text-slate-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"><Trash2 className="w-4 h-4" /></button>
                        <input type="text" placeholder="Project Name" value={project.project_name} onChange={(e) => handleProjectChange(index, "project_name", e.target.value)} className="w-full bg-transparent border-b border-slate-800 pb-1 text-sm text-slate-200 outline-none focus:border-blue-500 mb-2" />
                        <div className="flex gap-2">
                          <input type="text" placeholder="NAICS" value={project.naics_codes} onChange={(e) => handleProjectChange(index, "naics_codes", e.target.value)} className="w-1/2 bg-slate-900 border border-slate-800 rounded p-1.5 text-xs text-slate-200 outline-none" />
                          <input type="text" placeholder="Standards" value={project.standards} onChange={(e) => handleProjectChange(index, "standards", e.target.value)} className="w-1/2 bg-slate-900 border border-slate-800 rounded p-1.5 text-xs text-slate-200 outline-none" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <Button onClick={startAgentPipeline} disabled={isGenerating} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-6 rounded-xl shadow-lg">
                  {isGenerating ? <><Bot className="w-5 h-5 mr-2 animate-spin" /> Agents Working...</> : <><Bot className="w-5 h-5 mr-2" /> Run AI Pipeline</>}
                </Button>
              </CardContent>
            </Card>

            {/* ALIGNMENT FIX: flex-grow makes this stretch to the bottom */}
            <Card className="bg-slate-900 border-slate-800 shadow-xl hidden lg:flex flex-col flex-grow">
              <CardHeader className="pb-3 shrink-0">
                <CardTitle className="text-slate-200 text-sm flex items-center font-bold tracking-wide">
                  <Server className="w-4 h-4 mr-2 text-indigo-400" />
                  System Architecture
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-5 flex-grow">
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400 flex items-center"><Database className="w-4 h-4 mr-2 text-slate-500"/> Vector Engine</span>
                    <span className="text-green-400 font-mono bg-green-500/10 px-2 py-1 rounded">FAISS Online</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400 flex items-center"><Share2 className="w-4 h-4 mr-2 text-slate-500"/> Graph Topology</span>
                    <span className="text-green-400 font-mono bg-green-500/10 px-2 py-1 rounded">NetworkX Active</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400 flex items-center"><Brain className="w-4 h-4 mr-2 text-slate-500"/> Inference Agent</span>
                    <span className="text-blue-400 font-mono bg-blue-500/10 px-2 py-1 rounded">Local LLM</span>
                  </div>
                </div>

                <Separator className="bg-slate-800" />

                <div>
                  <p className="text-xs text-slate-400 uppercase font-bold tracking-widest mb-3">Multi-Agent Workflow</p>
                  <div className="relative border-l-2 border-slate-800 ml-2 space-y-4 pb-1">
                     <div className="relative pl-4">
                       <div className="absolute -left-[9px] top-1.5 w-4 h-4 bg-slate-900 border-2 border-slate-500 rounded-full"></div>
                       <p className="text-xs text-slate-200 font-bold">1. Context Extraction</p>
                       <p className="text-[11px] text-slate-500 mt-0.5">RFP chunking & Graph traversal</p>
                     </div>
                     <div className="relative pl-4">
                       <div className="absolute -left-[9px] top-1.5 w-4 h-4 bg-slate-900 border-2 border-slate-500 rounded-full"></div>
                       <p className="text-xs text-slate-200 font-bold">2. Drafter Agent</p>
                       <p className="text-[11px] text-slate-500 mt-0.5">Generates strict compliance draft</p>
                     </div>
                     <div className="relative pl-4">
                       <div className="absolute -left-[9px] top-1.5 w-4 h-4 bg-slate-900 border-2 border-blue-500 rounded-full shadow-[0_0_8px_rgba(59,130,246,0.6)]"></div>
                       <p className="text-xs text-slate-200 font-bold">3. Auditor Agent</p>
                       <p className="text-[11px] text-slate-500 mt-0.5">Red-teams draft & forces rewrites</p>
                     </div>
                  </div>
                </div>
              </CardContent>
            </Card>

          </div>

          {/* RIGHT COLUMN: Flex layout */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            
            {/* PROGRESS FIX: Glowing Neon Progress Bar */}
            {(isGenerating || progress > 0) && (
              <Card className="bg-slate-900 border-slate-800 shadow-xl shrink-0">
                <CardContent className="pt-6">
                  <div className="flex justify-between items-center mb-4">
                    <p className="text-sm font-mono text-cyan-400 flex items-center gap-2">
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                      </span>
                      {statusText}
                    </p>
                    <span className="text-xs font-mono text-slate-400">{progress}%</span>
                  </div>
                  
                  {/* The Glowing Bar */}
                  <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                    <div 
                      className="h-full bg-gradient-to-r from-blue-600 to-cyan-400 shadow-[0_0_12px_rgba(34,211,238,0.8)] transition-all duration-500 ease-out"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </CardContent>
              </Card>
            )}

            {result ? (
              <div className="flex flex-col gap-6 flex-grow">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 shrink-0">
                  <Card className="bg-slate-900 border-slate-800 shadow-xl">
                    <CardContent className="pt-6 flex items-center gap-4">
                      <div className="p-3 bg-green-500/10 rounded-full border border-green-500/20"><CheckCircle className="w-8 h-8 text-green-400" /></div>
                      <div><p className="text-xs text-slate-400 uppercase font-bold tracking-widest">Compliance Score</p><p className="text-3xl font-bold text-slate-100">{result.final_compliance_score}/100</p></div>
                    </CardContent>
                  </Card>
                  <Card className="bg-slate-900 border-slate-800 shadow-xl">
                    <CardContent className="pt-6 flex items-center gap-4">
                      <div className="p-3 bg-blue-500/10 rounded-full border border-blue-500/20"><Activity className="w-8 h-8 text-blue-400" /></div>
                      <div><p className="text-xs text-slate-400 uppercase font-bold tracking-widest">Agent Iterations</p><p className="text-3xl font-bold text-slate-100">{result.iterations_required}</p></div>
                    </CardContent>
                  </Card>
                </div>

                {result.auditor_notes && (
                  <Card className="bg-slate-900 border-amber-500/30 shadow-xl shrink-0">
                    <CardHeader className="pb-2"><CardTitle className="text-amber-400 text-base flex items-center font-bold tracking-wide"><ShieldAlert className="w-5 h-5 mr-2" /> AI Auditor Notes</CardTitle></CardHeader>
                    <CardContent><p className="text-slate-300 text-sm leading-relaxed">{result.auditor_notes}</p></CardContent>
                  </Card>
                )}

                {/* ALIGNMENT FIX: Editor flex-grow to snap to bottom */}
                <Card className="bg-slate-900 border-slate-800 shadow-xl flex flex-col flex-grow">
                  <CardHeader className="flex flex-row items-center justify-between border-b border-slate-800 pb-4 shrink-0">
                    <CardTitle className="text-slate-200 text-lg flex items-center"><FileText className="w-5 h-5 mr-2 text-cyan-400" /> Human-in-the-Loop Editor</CardTitle>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => {navigator.clipboard.writeText(editableDraft); alert("Copied!")}} className="h-8 border-slate-700 hover:bg-slate-800 text-slate-300"><Copy className="w-4 h-4 mr-2" /> Copy</Button>
                      <Button size="sm" onClick={handleExportWord} className="h-8 bg-blue-600 hover:bg-blue-500 text-white"><FileCode2 className="w-4 h-4 mr-2" /> Export .doc</Button>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-6 flex flex-col flex-grow">
                    <textarea 
                      value={editableDraft} 
                      onChange={(e) => setEditableDraft(e.target.value)} 
                      className="w-full flex-grow min-h-[400px] bg-slate-950 text-slate-300 text-sm leading-relaxed font-serif p-6 border border-slate-800 rounded-xl focus:border-blue-500 outline-none resize-none custom-scrollbar" 
                    />
                  </CardContent>
                </Card>
              </div>
            ) : (
              // ALIGNMENT FIX: Empty state flex-grow to snap to bottom
              <div className="border-2 border-dashed border-slate-800 rounded-2xl flex flex-col items-center justify-center text-slate-500 bg-slate-900/50 flex-grow min-h-[600px]">
                <div className="p-6 bg-slate-900 rounded-full mb-6 border border-slate-800"><Bot className="w-12 h-12 opacity-50" /></div>
                <p className="text-base font-medium tracking-wide">Awaiting Configuration</p>
                <p className="text-sm text-slate-500 mt-2">Upload your RFP and click Run AI Pipeline</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <footer className="border-t border-slate-800 bg-slate-900 py-6 mt-8 shrink-0">
        <div className="max-w-7xl mx-auto px-4 md:px-8 flex flex-col md:flex-row justify-between items-center gap-4 text-slate-500">
          <p className="text-xs font-mono">GOVPRENEURS v2.4 // PRODUCTION RELEASE</p>
          <div className="flex items-center gap-4">
            <span className="text-[10px] uppercase font-bold tracking-widest text-blue-500">Secure GovTech Architecture</span>
            <Separator orientation="vertical" className="h-4 bg-slate-700 hidden md:block" />
            <p className="text-xs hidden md:block">© 2026 Developed for GovPreneurs Case Study</p>
          </div>
        </div>
      </footer>
      
      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar { width: 8px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #475569; }
      `}</style>
    </div>
  );
}