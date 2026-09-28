import { create } from "zustand";

interface UIStore {
  isSidebarOpen: boolean;
  isMobileSidebarOpen: boolean;
  isSearchOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setMobileSidebarOpen: (open: boolean) => void;
  setSearchOpen: (open: boolean) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  isSidebarOpen: true,
  isMobileSidebarOpen: false,
  isSearchOpen: false,

  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setSidebarOpen: (open) => set({ isSidebarOpen: open }),
  setMobileSidebarOpen: (open) => set({ isMobileSidebarOpen: open }),
  setSearchOpen: (open) => set({ isSearchOpen: open }),
}));
