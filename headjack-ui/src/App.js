import './App.css';
import Sidebar from './components/sidebar';
import AppRouter from './AppRouter'

function App() {
  return (
    <div className="flex">
      <Sidebar />
      <AppRouter />
    </div>
  );
}

export default App;
