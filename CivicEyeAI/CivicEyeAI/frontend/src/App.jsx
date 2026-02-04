
import { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, AlertTriangle, Clock, Banknote, Activity, CheckCircle, ShieldCheck, FileText, Send } from 'lucide-react';

function App() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [roadType, setRoadType] = useState('MainRoad');
    const [trafficLevel, setTrafficLevel] = useState('Medium');
    const [issueType, setIssueType] = useState('Pothole');

    // Pipeline States
    const [stage, setStage] = useState('idle'); // idle, analyzing, verifying, processing, complete
    const [analysis, setAnalysis] = useState(null);
    const [verification, setVerification] = useState(null);
    const [reward, setReward] = useState(null);
    const [workOrder, setWorkOrder] = useState(null);
    const [emailStatus, setEmailStatus] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedFile(file);
            setPreviewUrl(URL.createObjectURL(file));
            resetPipeline();
        }
    };

    const resetPipeline = () => {
        setAnalysis(null);
        setVerification(null);
        setReward(null);
        setWorkOrder(null);
        setEmailStatus(null);
        setStage('idle');
        setError(null);
    };

    const runFullPipeline = async () => {
        if (!selectedFile) return;

        setStage('analyzing');
        setError(null);

        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('road_type', roadType);
        formData.append('traffic_level', trafficLevel);
        formData.append('issue_type', issueType.toLowerCase());

        try {
            // 1. ANALYZE (Vision + Agent)
            const analyzeRes = await axios.post('http://localhost:8000/analyze', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            setAnalysis(analyzeRes.data);

            // 2. VERIFY
            setStage('verifying');
            const verifyRes = await axios.post('http://localhost:8000/verify', {
                vision_confidence: analyzeRes.data.vision_confidence || 0.85, // Fallback if backend doesn't send
                agent_result: analyzeRes.data,
                location: { lat: 12.9716, lon: 77.5946 } // Mock location for demo
            });
            setVerification(verifyRes.data);

            if (verifyRes.data.is_verified) {
                setStage('processing');

                // 3. REWARD
                const rewardRes = await axios.post('http://localhost:8000/reward', {
                    report_id: verifyRes.data.report_id,
                    report_data: {
                        ...analyzeRes.data,
                        issue_type: issueType.toLowerCase(),
                        verification_status: verifyRes.data.verification_status
                    },
                    user_id: "demo_user_001"
                });
                setReward(rewardRes.data);

                // 4. WORK ORDER & ACTION (Only if High Priority)
                if (['High', 'Critical'].includes(analyzeRes.data.priority)) {
                    const woRes = await axios.post('http://localhost:8000/work-order', {
                        report_id: verifyRes.data.report_id,
                        location: { lat: 12.9716, lon: 77.5946, address: "MG Road, Bangalore" },
                        agent_decision: { ...analyzeRes.data, issue_type: issueType.toLowerCase() }
                    });
                    setWorkOrder(woRes.data);

                    // 5. EMAIL DISPATCH
                    if (woRes.data) {
                        const emailRes = await axios.post('http://localhost:8000/dispatch-email', {
                            work_order_data: woRes.data
                        });
                        setEmailStatus(emailRes.data);
                    }
                }
            }

            setStage('complete');

        } catch (err) {
            console.error(err);
            setError("Pipeline failed. Check backend logs.");
            setStage('idle');
        }
    };

    // Helper for status colors
    const getRiskColor = (score) => {
        if (score >= 80) return 'text-red-600 bg-red-100 border-red-200';
        if (score >= 40) return 'text-amber-600 bg-amber-100 border-amber-200';
        return 'text-green-600 bg-green-100 border-green-200';
    };

    return (
        <div className="min-h-screen bg-gray-50 text-slate-800 font-sans pb-10">
            {/* Header */}
            <header className="bg-slate-900 text-white py-6 shadow-md sticky top-0 z-50">
                <div className="container mx-auto px-6 flex justify-between items-center">
                    <div>
                        <h1 className="text-2xl font-bold flex items-center gap-2">
                            <span className="text-blue-400">👁️</span> Civic-Eye AI
                        </h1>
                        <p className="text-slate-400 text-xs tracking-wide uppercase mt-1">Autonomous Infrastructure Operations</p>
                    </div>
                    <div className="flex gap-4 text-xs font-mono text-slate-400">
                        <span>v2.0-Agentic</span>
                        <span className={stage !== 'idle' && stage !== 'complete' ? "text-blue-400 animate-pulse" : "text-green-500"}>
                            Status: {stage === 'idle' ? 'Ready' : stage === 'complete' ? 'Done' : 'Processing...'}
                        </span>
                    </div>
                </div>
            </header>

            <main className="container mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">

                {/* LEFT: INPUTS */}
                <div className="lg:col-span-4 space-y-6">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                        <h2 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 border-b pb-2">1. Field Report</h2>

                        {/* Image Input */}
                        <div className="mb-6 relative group">
                            <input type="file" accept="image/*" onChange={handleFileChange} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" />
                            <div className={`border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center transition-colors ${previewUrl ? 'border-blue-300 bg-blue-50' : 'border-slate-300 hover:bg-slate-50'}`}>
                                {previewUrl ? (
                                    <img src={previewUrl} className="max-h-48 object-contain rounded shadow-sm" alt="Preview" />
                                ) : (
                                    <>
                                        <Upload className="w-8 h-8 text-slate-400 mb-2" />
                                        <p className="text-sm text-slate-500">Upload site photo</p>
                                    </>
                                )}
                            </div>
                        </div>

                        {/* Selectors */}
                        <div className="grid grid-cols-1 gap-4">
                            <div>
                                <label className="text-xs font-semibold text-slate-500">Infrastructure Type</label>
                                <select value={issueType} onChange={(e) => setIssueType(e.target.value)} className="w-full mt-1 p-2 bg-slate-50 border rounded text-sm">
                                    <option value="Pothole">Pothole</option>
                                    <option value="Street Light">Street Light</option>
                                    <option value="Garbage">Garbage Dump</option>
                                </select>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-xs font-semibold text-slate-500">Road Class</label>
                                    <select value={roadType} onChange={(e) => setRoadType(e.target.value)} className="w-full mt-1 p-2 bg-slate-50 border rounded text-sm">
                                        <option value="Highway">Highway</option>
                                        <option value="MainRoad">Main Road</option>
                                        <option value="Residential">Residential</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="text-xs font-semibold text-slate-500">Traffic Density</label>
                                    <select value={trafficLevel} onChange={(e) => setTrafficLevel(e.target.value)} className="w-full mt-1 p-2 bg-slate-50 border rounded text-sm">
                                        <option value="Low">Low</option>
                                        <option value="Medium">Medium</option>
                                        <option value="High">High</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        {/* Run Button */}
                        <button
                            onClick={runFullPipeline}
                            disabled={!selectedFile || (stage !== 'idle' && stage !== 'complete')}
                            className="w-full mt-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white rounded-lg font-medium shadow-lg shadow-blue-500/20 transition-all flex justify-center items-center gap-2"
                        >
                            {stage === 'analyzing' ? <Activity className="animate-spin w-5 h-5" /> : <Send className="w-5 h-5" />}
                            {stage === 'idle' || stage === 'complete' ? 'Process Report' : 'Analyzing...'}
                        </button>

                        {error && <div className="mt-4 p-3 bg-red-50 text-red-700 text-xs rounded border border-red-200">{error}</div>}
                    </div>
                </div>

                {/* RIGHT: DASHBOARD */}
                <div className="lg:col-span-8 space-y-6">

                    {/* 1. AGENT DECISION PANEL */}
                    {analysis && (
                        <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden animate-fade-in-up">
                            <div className="bg-slate-50 px-6 py-3 border-b border-slate-100 flex justify-between items-center">
                                <h2 className="text-sm font-bold text-slate-700 flex items-center gap-2">
                                    <Activity className="w-4 h-4 text-blue-500" /> Civic Cortex Decision
                                </h2>
                                <span className="text-xs font-mono text-slate-400">conf: {(analysis.confidence_score * 100).toFixed(1)}%</span>
                            </div>
                            <div className="p-6">
                                <div className="flex items-start gap-6">
                                    {/* Annotated Image */}
                                    <div className="w-1/3">
                                        <img src={analysis.annotated_image} className="w-full rounded-lg border border-slate-200" alt="Analyzed" />
                                        <div className="mt-2 text-center text-xs text-slate-500">{analysis.damaged_area_m2} m² detected area</div>
                                    </div>

                                    {/* Metrics */}
                                    <div className="flex-1 space-y-4">
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <div className="text-xs text-slate-400 uppercase">Risk Score</div>
                                                <div className={`text-3xl font-bold ${getRiskColor(analysis.risk_score).split(' ')[0]}`}>
                                                    {analysis.risk_score}
                                                    <span className="text-sm text-slate-400 font-normal">/100</span>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold border ${analysis.priority === 'Critical' ? 'bg-red-600 text-white border-red-600' : 'bg-blue-100 text-blue-700 border-blue-200'}`}>
                                                    {analysis.priority} Priority
                                                </span>
                                            </div>
                                        </div>

                                        <div className="p-3 bg-slate-50 rounded border border-slate-100">
                                            <div className="text-xs font-bold text-slate-600 mb-1">RECOMMENDED ACTION</div>
                                            <p className="text-sm text-slate-800">{analysis.recommended_action}</p>
                                        </div>

                                        <p className="text-xs text-slate-500 italic">"{analysis.decision_explanation}"</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* 2. VERIFICATION & REWARDS */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {verification && (
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 animate-fade-in-up">
                                <h3 className="text-xs font-bold text-slate-500 uppercase mb-3 flex items-center gap-2">
                                    <ShieldCheck className="w-4 h-4" /> Verification Status
                                </h3>
                                <div className={`p-4 rounded-lg border flex items-center gap-3 ${verification.is_verified ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                                    {verification.is_verified ? <CheckCircle className="text-green-600 w-6 h-6" /> : <AlertTriangle className="text-red-600 w-6 h-6" />}
                                    <div>
                                        <div className={`font-bold ${verification.is_verified ? 'text-green-800' : 'text-red-800'}`}>
                                            {verification.verification_status.replace('_', ' ').toUpperCase()}
                                        </div>
                                        <div className="text-xs text-slate-600">{verification.verification_reason}</div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {reward && (
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 animate-fade-in-up delay-100">
                                <h3 className="text-xs font-bold text-slate-500 uppercase mb-3 flex items-center gap-2">
                                    <Banknote className="w-4 h-4" /> Citizen Rewards
                                </h3>
                                {reward.status === 'success' ? (
                                    <div className="text-center py-2">
                                        <div className="text-3xl font-bold text-blue-600">+{reward.points_awarded} pts</div>
                                        <div className="text-xs text-slate-500 mt-1">Trust Score updated to <span className="font-bold text-slate-800">{reward.new_trust_score.toFixed(1)}</span></div>
                                    </div>
                                ) : (
                                    <div className="text-center py-2 text-slate-400 text-sm">No rewards issued.</div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* 3. GOVERNMENT ACTION (Work Order) */}
                    {workOrder && (
                        <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden animate-fade-in-up delay-200">
                            <div className="bg-slate-800 text-white px-6 py-3 flex justify-between items-center">
                                <h2 className="text-sm font-bold flex items-center gap-2">
                                    <FileText className="w-4 h-4 text-amber-400" /> Government Action Initiated
                                </h2>
                                <div className="text-xs bg-slate-700 px-2 py-1 rounded">ID: {workOrder.work_order_id}</div>
                            </div>

                            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="font-mono text-xs text-slate-600 bg-slate-50 p-4 rounded border border-slate-200 whitespace-pre-wrap h-40 overflow-y-auto">
                                    {workOrder.text_preview}
                                </div>

                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <div className="flex justify-between text-sm py-1 border-b border-slate-100">
                                            <span className="text-slate-500">Department</span>
                                            <span className="font-medium text-slate-800 text-right">{workOrder.pdf_data.header.department}</span>
                                        </div>
                                        <div className="flex justify-between text-sm py-1 border-b border-slate-100">
                                            <span className="text-slate-500">Est. Budget</span>
                                            <span className="font-medium text-slate-800">INR {workOrder.pdf_data.budget.estimated_inr}</span>
                                        </div>
                                        <div className="flex justify-between text-sm py-1 border-b border-slate-100">
                                            <span className="text-slate-500">Timeline</span>
                                            <span className="font-medium text-slate-800">{analysis.repair_time_days} Days</span>
                                        </div>
                                    </div>

                                    {/* Email Status */}
                                    {emailStatus && (
                                        <div className={`mt-4 p-3 rounded text-xs flex items-center gap-2 ${emailStatus.status === 'sent' || emailStatus.status === 'mocked' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                            <Send className="w-3 h-3" />
                                            {emailStatus.status === 'mocked' ? 'Email dispatched to authority (Simulation)' : emailStatus.msg}
                                        </div>
                                    )}

                                    <button className="w-full py-2 border border-slate-300 rounded text-slate-600 text-xs font-medium hover:bg-slate-50 transition-colors">
                                        Download Official PDF
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                </div>
            </main>
        </div>
    );
}

export default App;
