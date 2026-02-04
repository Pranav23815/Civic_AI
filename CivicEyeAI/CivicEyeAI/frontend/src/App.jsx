
import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Upload, AlertTriangle, Clock, Banknote, Activity, CheckCircle, ShieldCheck, FileText, Send, Download, Share2, MapPin, TrendingUp } from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix Leaflet marker icon issue in React
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

// Safe Leaflet Icon Fix
const DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

function App() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [roadType, setRoadType] = useState('MainRoad');
    const [trafficLevel, setTrafficLevel] = useState('Medium');
    const [issueType, setIssueType] = useState('Pothole');

    // Location State
    const [location, setLocation] = useState({ lat: 12.9716, lon: 77.5946 }); // Default Bangalore
    const [locStatus, setLocStatus] = useState('default'); // default, locating, found, error

    // Pipeline States
    const [stage, setStage] = useState('idle'); // idle, analyzing, verifying, processing, complete
    const [analysis, setAnalysis] = useState(null);
    const [verification, setVerification] = useState(null);
    const [reward, setReward] = useState(null);
    const [workOrder, setWorkOrder] = useState(null);
    const [emailStatus, setEmailStatus] = useState(null);
    const [error, setError] = useState(null);

    // Auto-Download Effect
    useEffect(() => {
        if (workOrder && workOrder.pdf_data) {
            downloadPDF();
        }
    }, [workOrder]);

    // Get Location on Mount
    useEffect(() => {
        if (navigator.geolocation) {
            setLocStatus('locating');
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    setLocation({
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    });
                    setLocStatus('found');
                },
                (err) => {
                    console.error("Geo Error", err);
                    setLocStatus('error');
                }
            );
        }
    }, []);

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
                vision_confidence: analyzeRes.data.vision_confidence || 0.85,
                agent_result: analyzeRes.data,
                location: location // Use Real Location
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
                        location: { ...location, address: "Detected via GPS" },
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

    const downloadPDF = async () => {
        if (!workOrder || !workOrder.pdf_data) return;
        try {
            const response = await axios.post('http://localhost:8000/generate-pdf', workOrder.pdf_data, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `WorkOrder_${workOrder.work_order_id}.pdf`);
            document.body.appendChild(link);
            link.click();
        } catch (e) {
            console.error("PDF Download failed", e);
        }
    };

    const shareWhatsApp = () => {
        if (!analysis) return;
        const text = `🚨 *Civic-Eye Alert* 🚨\n\nIssue: ${issueType}\nPriority: ${analysis.priority}\nRisk Score: ${analysis.risk_score}/100\nLocation: https://maps.google.com/?q=${location.lat},${location.lon}\n\nView details on dashboard.`;
        window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
    };

    // Helper for status colors
    const getRiskColor = (score) => {
        if (score >= 80) return 'text-red-600 bg-red-100 border-red-200';
        if (score >= 40) return 'text-amber-600 bg-amber-100 border-amber-200';
        return 'text-green-600 bg-green-100 border-green-200';
    };

    // Calculate Potential Savings
    const getSavings = (cost, risk) => {
        if (!cost) return 0;
        return Math.round(cost * (risk / 100) * 1.5);
    };

    return (
        <div className="min-h-screen bg-slate-50 text-slate-800 font-sans pb-10">
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
                        <span>v2.2-LiveGPS</span>
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

                        {/* MAP WIDGET */}
                        <div className="mt-6">
                            <h3 className="text-xs font-bold text-slate-500 uppercase mb-2 flex justify-between">
                                Location Lock
                                <span className={`text-[10px] px-2 py-0.5 rounded-full ${locStatus === 'found' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                                    {locStatus === 'found' ? 'GPS Active' : locStatus === 'locating' ? 'Locating...' : 'Default'}
                                </span>
                            </h3>
                            <div className="h-48 w-full rounded-lg overflow-hidden border border-slate-200 z-0 relative flex items-center justify-center bg-slate-100">
                                <p className="text-xs text-slate-400">Map visualization disabled (GPS still active)</p>
                                {/* 
                                <MapContainer key={`${location.lat}-${location.lon}`} center={[location.lat, location.lon]} zoom={15} scrollWheelZoom={false} style={{ height: '100%', width: '100%' }}>
                                    <TileLayer
                                        attribution='&copy; OpenStreetMap contributors'
                                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                    />
                                    <Marker position={[location.lat, location.lon]}>
                                        <Popup>
                                            Issue Location <br /> {location.lat.toFixed(4)}, {location.lon.toFixed(4)}
                                        </Popup>
                                    </Marker>
                                </MapContainer>
                                */}
                            </div>
                        </div>

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
                                <div className="flex gap-2">
                                    <button onClick={shareWhatsApp} className="flex items-center gap-1 px-3 py-1 bg-green-500 hover:bg-green-600 text-white text-xs rounded transition-colors">
                                        <Share2 className="w-3 h-3" /> Share
                                    </button>
                                    <span className="text-xs font-mono text-slate-400 pt-1">conf: {(analysis.confidence_score * 100).toFixed(1)}%</span>
                                </div>
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

                                        {/* SMART INSIGHT */}
                                        <div className="flex items-center gap-3 p-3 bg-indigo-50 border border-indigo-100 rounded-lg">
                                            <div className="bg-indigo-100 p-2 rounded-full">
                                                <TrendingUp className="w-4 h-4 text-indigo-600" />
                                            </div>
                                            <div className="text-xs">
                                                <span className="font-bold text-slate-700">Economic Impact: </span>
                                                <span className="text-slate-600">
                                                    Repairing now saves <span className="font-bold text-green-600">~₹{getSavings(analysis.estimated_cost, analysis.risk_score)}</span> compared to delaying 30 days.
                                                </span>
                                            </div>
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

                                    <button
                                        onClick={downloadPDF}
                                        className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-white rounded text-xs font-medium transition-colors flex justify-center items-center gap-2"
                                    >
                                        <Download className="w-4 h-4" /> Download Official PDF
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
