import { useState } from 'react';
import axios from 'axios';
import { Upload, AlertTriangle, Clock, Banknote, Activity } from 'lucide-react';

function App() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [roadType, setRoadType] = useState('MainRoad');
    const [trafficLevel, setTrafficLevel] = useState('Medium');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedFile(file);
            setPreviewUrl(URL.createObjectURL(file));
            setResult(null); // Reset previous result
            setError(null);
        }
    };

    const handleAnalyze = async () => {
        if (!selectedFile) return;

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('road_type', roadType);
        formData.append('traffic_level', trafficLevel);

        try {
            // Assuming backend is running on localhost:8000
            const response = await axios.post('http://localhost:8000/analyze', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setResult(response.data);
        } catch (err) {
            console.error(err);
            setError("Analysis failed. Ensure backend is running.");
        } finally {
            setLoading(false);
        }
    };

    // Badge Color Logic
    const getSeverityColor = (level) => {
        if (level === 'High') return 'bg-red-100 text-red-800 border-red-200';
        if (level === 'Medium') return 'bg-yellow-100 text-yellow-800 border-yellow-200';
        return 'bg-green-100 text-green-800 border-green-200';
    };

    const getPriorityColor = (level) => {
        if (level === 'High') return 'bg-red-600 text-white';
        if (level === 'Medium') return 'bg-orange-500 text-white';
        return 'bg-blue-500 text-white';
    };

    return (
        <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
            {/* Header */}
            <header className="bg-slate-900 text-white py-6 shadow-md">
                <div className="container mx-auto px-6">
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <span className="text-blue-400">👁️</span> Civic-Eye AI
                    </h1>
                    <p className="text-slate-400 text-sm mt-1">
                        Autonomous Urban Infrastructure Decision System
                    </p>
                </div>
            </header>

            <main className="container mx-auto px-6 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

                    {/* LEFT PANEL - Controls */}
                    <div className="lg:col-span-4 space-y-6">
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <h2 className="text-lg font-semibold mb-4 text-slate-800">1. Input Data</h2>

                            {/* Image Upload */}
                            <div className="mb-6">
                                <label className="block text-sm font-medium text-gray-700 mb-2">Road Image</label>
                                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 flex flex-col items-center justify-center text-center hover:bg-gray-50 transition-colors cursor-pointer relative">
                                    <input
                                        type="file"
                                        accept="image/*"
                                        onChange={handleFileChange}
                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                    />
                                    <Upload className="w-8 h-8 text-gray-400 mb-2" />
                                    <p className="text-sm text-gray-500">
                                        {selectedFile ? selectedFile.name : "Click to upload image"}
                                    </p>
                                </div>
                            </div>

                            {/* Selectors */}
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Road Type</label>
                                    <select
                                        value={roadType}
                                        onChange={(e) => setRoadType(e.target.value)}
                                        className="w-full p-2.5 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                                    >
                                        <option value="Highway">Highway</option>
                                        <option value="MainRoad">Main Road</option>
                                        <option value="Residential">Residential</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Traffic Level</label>
                                    <select
                                        value={trafficLevel}
                                        onChange={(e) => setTrafficLevel(e.target.value)}
                                        className="w-full p-2.5 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                                    >
                                        <option value="Low">Low</option>
                                        <option value="Medium">Medium</option>
                                        <option value="High">High</option>
                                    </select>
                                </div>
                            </div>

                            {/* Action Button */}
                            <button
                                onClick={handleAnalyze}
                                disabled={!selectedFile || loading}
                                className={`w-full mt-6 py-3 px-4 rounded-lg font-medium text-white transition-all 
                  ${!selectedFile || loading
                                        ? 'bg-gray-400 cursor-not-allowed'
                                        : 'bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/30'
                                    }`}
                            >
                                {loading ? (
                                    <span className="flex items-center justify-center gap-2">
                                        <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Analyzing...
                                    </span>
                                ) : 'Analyze Infrastructure'}
                            </button>
                        </div>
                    </div>

                    {/* RIGHT PANEL - Results */}
                    <div className="lg:col-span-8 space-y-6">

                        {/* Disclaimer */}
                        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
                            <p className="text-sm text-blue-800">
                                ℹ️ All predictions are generated by a learning-based decision agent trained on real municipal infrastructure data.
                            </p>
                        </div>

                        {error && (
                            <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
                                <p className="text-sm text-red-800">{error}</p>
                            </div>
                        )}

                        {/* AI Vision Preview */}
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 min-h-[300px] flex flex-col">
                            <h2 className="text-lg font-semibold mb-4 text-slate-800">2. AI Vision Analysis</h2>
                            <div className="flex-1 bg-gray-100 rounded-lg overflow-hidden flex items-center justify-center relative">
                                {result?.annotated_image ? (
                                    <img
                                        src={result.annotated_image}
                                        alt="Analyzed"
                                        className="max-h-[500px] w-full object-contain"
                                    />
                                ) : previewUrl ? (
                                    <img
                                        src={previewUrl}
                                        alt="Preview"
                                        className="max-h-[500px] w-full object-contain opacity-50 filter blur-[1px]"
                                    />
                                ) : (
                                    <div className="text-gray-400 flex flex-col items-center">
                                        <Activity className="w-12 h-12 mb-2 opacity-20" />
                                        <span>No image loaded</span>
                                    </div>
                                )}
                                {loading && (
                                    <div className="absolute inset-0 bg-white/50 backdrop-blur-sm flex items-center justify-center">
                                        <div className="bg-white px-4 py-2 rounded-full shadow-lg text-sm font-medium text-slate-600 animate-pulse">
                                            Detecting Potholes & Measuring Area...
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Decision Cards */}
                        {result && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {/* Priority & Severity */}
                                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                                    <h3 className="text-sm font-medium text-gray-500 mb-4 uppercase tracking-wider">Assessment</h3>
                                    <div className="space-y-4">
                                        <div className="flex justify-between items-center">
                                            <span className="text-gray-700 font-medium">Severity</span>
                                            <span className={`px-3 py-1 rounded-full text-sm font-bold border ${getSeverityColor(result.severity)}`}>
                                                {result.severity}
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-1.5 dark:bg-gray-100">
                                            <div className={`h-1.5 rounded-full ${result.severity === 'High' ? 'w-full bg-red-500' : result.severity === 'Medium' ? 'w-2/3 bg-yellow-500' : 'w-1/3 bg-green-500'}`}></div>
                                        </div>

                                        <div className="flex justify-between items-center pt-2">
                                            <span className="text-gray-700 font-medium">Action Priority</span>
                                            <span className={`px-3 py-1 rounded-full text-sm font-bold shadow-sm ${getPriorityColor(result.priority)}`}>
                                                {result.priority} Priority
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Logistics */}
                                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                                    <h3 className="text-sm font-medium text-gray-500 mb-4 uppercase tracking-wider">Logistics & Cost</h3>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                                            <div className="flex items-center gap-2 mb-1">
                                                <Banknote className="w-4 h-4 text-green-600" />
                                                <span className="text-xs font-medium text-gray-500">Est. Cost</span>
                                            </div>
                                            <p className="text-xl font-bold text-slate-900">{result.estimated_cost}</p>
                                        </div>

                                        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                                            <div className="flex items-center gap-2 mb-1">
                                                <Clock className="w-4 h-4 text-blue-600" />
                                                <span className="text-xs font-medium text-gray-500">Repair Time</span>
                                            </div>
                                            <p className="text-xl font-bold text-slate-900">{result.repair_time_days} <span className="text-sm font-normal text-gray-600">Days</span></p>
                                        </div>
                                    </div>

                                    <div className="mt-4 text-xs text-gray-400 text-center">
                                        Based on {result.damaged_area_m2} m² damaged area
                                    </div>
                                </div>
                            </div>
                        )}

                    </div>
                </div>
            </main>
        </div>
    );
}

export default App;
