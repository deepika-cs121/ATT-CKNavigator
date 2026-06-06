import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { TacticProvider } from './context/TacticContext.tsx';
import { AttackProvider } from './context/AttackContext';
import { Landing } from './pages/Landing.tsx';
import { RedTeam } from './pages/RedTeam.tsx';
import { BlueTeam } from './pages/BlueTeam.tsx';
import './index.css';
import { Toaster } from 'react-hot-toast';

export const App = () => {
  return (
    <Router>
      <TacticProvider>
        <AttackProvider>
          <Toaster 
            position="bottom-right"
            toastOptions={{
              style: {
                background: '#1f2937', // gray-800
                color: '#e5e7eb', // gray-200
                border: '1px solid #374151', // gray-700
              },
            }}
          />
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/red-team" element={<RedTeam />} />
            <Route path="/blue-team" element={<BlueTeam />} />
          </Routes>
        </AttackProvider>
      </TacticProvider>
    </Router>
  );
};

export default App;