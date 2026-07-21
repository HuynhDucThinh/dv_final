/**
 * Better Auth — Client-side configuration
 * Export các hooks và functions dùng trong React components:
 *   - useSession()     → lấy session hiện tại
 *   - signIn.*         → đăng nhập
 *   - signUp.*         → đăng ký
 *   - signOut()        → đăng xuất
 */
import { createAuthClient } from 'better-auth/react';

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',
});

export const {
  useSession,
  signIn,
  signUp,
  signOut,
} = authClient;
