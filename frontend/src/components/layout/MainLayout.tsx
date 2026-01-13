import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function MainLayout() {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-transparent font-sans">
      {/* Ambient background glow */}
      {/* <div className="fixed inset-0 pointer-events-none z-[-1] bg-cyber-grid opacity-20" /> -> Moved to global CSS body */}

      <Sidebar />
      <main className="flex-1 overflow-auto relative scroll-smooth custom-scrollbar">
        {/* Top fade for scrolling content */}
        <div className="sticky top-0 h-10 bg-gradient-to-b from-background to-transparent z-20 pointer-events-none" />

        <div className="container mx-auto p-6 md:p-8 max-w-[1600px] animate-fade-in-up">
          <Outlet />
        </div>

        {/* Bottom fade */}
        <div className="sticky bottom-0 h-10 bg-gradient-to-t from-background to-transparent z-20 pointer-events-none" />
      </main>
    </div>
  );
}
