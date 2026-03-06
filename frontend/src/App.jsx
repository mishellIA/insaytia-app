import { useState, useEffect } from 'react'; // PRIDANÉ: useEffect
import axios from 'axios';
import { Activity, Brain, Send } from 'lucide-react';


// 1. Pomocné funkcie
const getScoreDetails = (score) => {
  if (score >= 5.0) return { color: '#22c55e', label: 'Vysoká', emoji: '🌟', text: 'prosperujúci a plný energie' };
  if (score >= 4.0) return { color: '#eab308', label: 'Stredná', emoji: '⚖️', text: 'vyrovnaná úroveň energie a živosti' };
  if (score >= 3.0) return { color: '#f97316', label: 'Mierna', emoji: '🧘', text: 'funguje obmedzene, priestor pre obnovu' };
  return { color: '#ef4444', label: 'Znížená', emoji: '🪫', text: 'čas na reštart' };
};


const getBarColor = (score) => {
  if (score < 3) return "#FA8072";
  if (score < 4) return "#FFD92F";
  if (score < 5) return "#ADFF2F";
  return "#66C2A5";                
};


const labels = {
  Uvedomovanie: "Sebavnímanie",
    Agentnost: "Agentnosť",
    Sustredenost: "Kognitívna sústredenosť",
    Smerovanie: "Autentické smerovanie",
    Tlak: "Tlak a kontrola",
    Vazby: "Sociálne väzby",
    Zdatnost: "Zdatnosť",
    Pochybnosti: "Pochybnosti",
    Izolacia: "Sociálna izolácia",
    Presadzovanie: "Účelové presadzovanie",
    Potreba_uznania: "Potreba uznania",
    Indiferentnost: "Indiferentnosť"
};


function App() {
  const [inputs, setInputs] = useState({
    Uvedomovanie: 3,
    Agentnost: 3,
    Sustredenost: 6,
    Smerovanie: 3,
    Tlak: 3,
    Vazby: 3,
    Zdatnost: 1,
    Pochybnosti: 1,
    Izolacia: 1,
    Presadzovanie: 2,
    Potreba_uznania: 3,
    Indiferentnost: 2
  });


  const [liveScore, setLiveScore] = useState(3.5);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);


  // 2. Live Sync s Backendom (Presný model)
  useEffect(() => {
    const getLivePrediction = async () => {
      try {
        // Voláme backend s parametrom only_score=true, aby sme nezaťažovali Gemini
        const response = await axios.post('https://insaytia-app.onrender.com/predict?only_score=true', inputs);
        if (response.data && response.data.score !== undefined) {
          setLiveScore(response.data.score);
        }
      } catch (error) {
        console.error("Live sync error:", error);
      }
    };


    const timeoutId = setTimeout(getLivePrediction, 150);
    return () => clearTimeout(timeoutId);
  }, [inputs]);


  const handleChange = (name, value) => {
    setInputs(prev => ({ ...prev, [name]: parseFloat(value) }));
  };


  const handlePredict = async () => {
    setLoading(true);
    try {
      const response = await axios.post('https://insaytia-app.onrender.com/predict', inputs);
      setResult(response.data);
    } catch (error) {
      console.error("Chyba:", error);
      alert("Backend nebeží! Skontroluj uvicorn.");
    }
    setLoading(false);
  };


  return (
    <div style={{ backgroundColor: '#f5f7fa', minHeight: '100vh', padding: '20px', fontFamily: 'sans-serif' }}>
      <div style={{ maxWidth: '700px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
       
        <h1 style={{ textAlign: 'center', color: '#1a365d' }}>Insaytia | Energia Check</h1>


        {/* --- SEKCIA 1: LIVE VIZUALIZÁCIA --- */}
        <div style={{ backgroundColor: '#fff', padding: '25px', borderRadius: '20px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
          <h3 style={{ margin: '0 0 15px 0', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            🔋⚡ Dynamická Vizualizácia (Live Model)
          </h3>
         
          <div style={{ position: 'relative', height: '40px', backgroundColor: '#edf2f7', borderRadius: '8px', overflow: 'hidden' }}>
            <div style={{
              height: '100%',
              width: `${(liveScore / 7) * 100}%`, 
              backgroundColor: getBarColor(liveScore), 
              transition: 'width 0.3s ease-out, background-color 0.3s'
            }} />
            {[1,2,3,4,5,6,7].map(num => (
              <div key={num} style={{ position: 'absolute', left: `${(num/7)*100}%`, top: 0, bottom: 0, width: '1px', backgroundColor: 'rgba(0,0,0,0.1)' }} />
            ))}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '5px', fontSize: '12px', color: '#718096' }}>
            <span>0</span>
            <span style={{ fontWeight: 'bold', color: getBarColor(liveScore) }}>
               Modelové skóre: {Number(liveScore).toFixed(2)}
            </span>
            <span>7</span>
          </div>
        </div>


        {/* --- SEKCIA 2: SLIDERY --- */}
        <div style={{ backgroundColor: '#fff', padding: '25px', borderRadius: '20px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {Object.keys(inputs)
              .filter(key => labels[key])
              .map((key) => (
                <div key={key}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px', fontSize: '14px' }}>
                  <span>{labels[key] || key}</span>
                  <strong>{inputs[key]}</strong>
                </div>
                <input
                  type="range"
                  min="1"
                  max={key === 'Sustredenost' ? "6" : "5"}
                  step="0.1"
                  value={inputs[key]}
                  onChange={(e) => handleChange(key, e.target.value)}
                  style={{ width: '100%', cursor: 'pointer', accentColor: getBarColor(liveScore) }}
                />
              </div>
            ))}
          </div>
         
          <button
            onClick={handlePredict}
            disabled={loading}
            style={{
              width: '100%', marginTop: '25px', padding: '15px', borderRadius: '12px',
              backgroundColor: '#1a365d', color: 'white', border: 'none', cursor: 'pointer',
              fontWeight: 'bold', fontSize: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px'
            }}
          >
            {loading ? 'Preskúmavam konfiguráciu...' : <><Send size={18} /> AI interpretácia konfigurácie</>}
          </button>
        </div>


        {/* --- SEKCIA 3: AI VÝSLEDOK --- */}
        {result && (
          <div style={{
            backgroundColor: '#fff', padding: '30px', borderRadius: '20px',
            borderLeft: `10px solid ${getScoreDetails(result.score).color}`,
            boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
          }}>
            <div style={{ textAlign: 'center', marginBottom: '20px' }}>
              <span style={{ fontSize: '40px' }}>{getScoreDetails(result.score).emoji}</span>
              <h2 style={{ color: getScoreDetails(result.score).color, margin: '5px 0' }}>
                Finálne skóre: {result.score} / 7
              </h2>
              <p style={{ fontWeight: 'bold', textTransform: 'uppercase', color: '#718096' }}>
                Úroveň: {getScoreDetails(result.score).label}
              </p>
            </div>
           
            <div style={{ backgroundColor: '#f8fafc', padding: '20px', borderRadius: '12px' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: 0 }}>
                <Brain size={20} color="#1a365d" /> Expertný vhľad mentora
              </h4>
              <p style={{ lineHeight: '1.7', color: '#2d3748', whiteSpace: 'pre-wrap' }}>
                {result.interpretation}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


export default App;


