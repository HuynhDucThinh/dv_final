/**
 * Better Auth — Next.js API Route Handler
 * Tất cả requests đến /api/auth/* đều được xử lý tại đây.
 * Better Auth tự động handle: login, register, logout, OAuth callback, session...
 */
import { auth } from '@/lib/auth';
import { toNextJsHandler } from 'better-auth/next-js';

export const { GET, POST } = toNextJsHandler(auth);
