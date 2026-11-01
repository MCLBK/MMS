import {create} from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {api} from '../services/api';
import type {User, TokenResponse} from '../types';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  login: async (email, password) => {
    const tokens = await api.post<TokenResponse>('/auth/login', {email, password});
    await AsyncStorage.setItem('access_token', tokens.access_token);
    await AsyncStorage.setItem('refresh_token', tokens.refresh_token);

    const user = await api.get<User>('/auth/me');
    set({user, isAuthenticated: true, isLoading: false});
  },

  logout: async () => {
    await AsyncStorage.multiRemove(['access_token', 'refresh_token']);
    set({user: null, isAuthenticated: false});
  },

  fetchUser: async () => {
    try {
      const token = await AsyncStorage.getItem('access_token');
      if (!token) {
        set({isLoading: false});
        return;
      }
      const user = await api.get<User>('/auth/me');
      set({user, isAuthenticated: true, isLoading: false});
    } catch {
      set({isLoading: false, isAuthenticated: false});
    }
  },
}));
