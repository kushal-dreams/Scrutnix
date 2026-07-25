import { useEffect, useState } from 'react';
import { Footer, GuideBot, Header, TopLiveTicker } from './components/Layout';
import { DEMO_REPORTS, DEMO_STATS } from './data/demoData';
import { AboutMethodology } from './pages/AboutMethodology';
import { Community } from './pages/Community';
import { Home } from './pages/Home';
import { JobAnalyzerPage } from './pages/JobAnalyzerPage';
import { ReportPage } from './pages/ReportPage';
import { Research } from './pages/Research';
import { StudentHub } from './pages/StudentHub';
import { api } from './services/api';

export function App() {
  const [user, setUser] = useState(null);
  const [view, setView] = useState('home');
  const [stats, setStats] = useState(DEMO_STATS);
  const [reports, setReports] = useState(DEMO_REPORTS);
  const [toast, setToast] = useState('');

  const notify = (message) => {
    setToast(message);
    setTimeout(() => setToast(''), 3200);
  };

  const refresh = async () => {
    try {
      const [statsData, reportsData] = await Promise.all([api('/stats'), api('/reports')]);
      setStats(statsData);
      if (reportsData?.reports) {
        setReports(reportsData.reports.length ? reportsData.reports : DEMO_REPORTS);
      }
    } catch (error) {
      console.warn('Backend connection warning:', error);
      setStats(DEMO_STATS);
      setReports(DEMO_REPORTS);
    }
  };

  useEffect(() => {
    refresh().catch(() => {});
    const token = localStorage.getItem('scrutinix_token');
    if (token) api('/auth/me').then((d) => setUser(d.user)).catch(() => localStorage.removeItem('scrutinix_token'));
  }, []);

  return (
    <div>
      <TopLiveTicker reports={reports} />
      <Header view={view} setView={setView} user={user} setUser={setUser} notify={notify} />
      {toast && <div className="toast">{toast}</div>}
      {view === 'home' && <Home stats={stats} reports={reports} refresh={refresh} setView={setView} notify={notify} />}
      {view === 'report' && <ReportPage user={user} refresh={refresh} notify={notify} setView={setView} />}
      {view === 'community' && <Community reports={reports} refresh={refresh} user={user} notify={notify} />}
      {view === 'analyzer' && <JobAnalyzerPage notify={notify} setView={setView} />}
      {view === 'student' && <StudentHub setView={setView} />}
      {view === 'research' && <Research />}
      {view === 'about' && <AboutMethodology setView={setView} />}
      <GuideBot setView={setView} />
      <Footer />
    </div>
  );
}
