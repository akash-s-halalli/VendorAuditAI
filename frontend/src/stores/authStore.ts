import { create } from 'zustand';
import netlifyIdentity from 'netlify-identity-widget';

interface AuthState {
  user: netlifyIdentity.User | null;
  isAuthenticated: boolean;

  // Actions
  login: () => void;
  signup: () => void;
  logout: () => void;
  init: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,

  login: () => {
    netlifyIdentity.open('login');
  },

  signup: () => {
    netlifyIdentity.open('signup');
  },

  logout: () => {
    netlifyIdentity.logout();
  },

  init: () => {
    // Initialize the widget
    netlifyIdentity.init(); // This will auto-detect if on the confirmation URL

    // Get current user if already logged in
    const currentUser = netlifyIdentity.currentUser();
    set({
      user: currentUser,
      isAuthenticated: !!currentUser
    });

    // Listen for events
    netlifyIdentity.on('login', (user) => {
      console.log('Netlify Identity: Login', user);
      set({ user, isAuthenticated: true });
      netlifyIdentity.close();
    });

    netlifyIdentity.on('logout', () => {
      console.log('Netlify Identity: Logout');
      set({ user: null, isAuthenticated: false });
    });

    netlifyIdentity.on('error', (err) => {
      console.error('Netlify Identity error', err);
    });
  },
}));
