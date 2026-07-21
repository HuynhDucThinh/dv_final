/**
 * Better Auth — Server-side configuration
 * Kết nối PostgreSQL qua Supabase, hỗ trợ:
 *   - Email/password (credentials)
 *   - Google OAuth
 */
import { betterAuth } from 'better-auth';
import { Pool } from 'pg';

// Better Auth nhận Pool trực tiếp (không wrap trong {db, type})
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
  max: 5,
  // Transaction Pooler (port 6543) compatibility
  statement_timeout: 30000,
  query_timeout: 30000,
});

export const auth = betterAuth({
  database: pool,  // ← Đúng format: Pool trực tiếp

  secret: process.env.BETTER_AUTH_SECRET!,

  baseURL: process.env.BETTER_AUTH_URL || 'http://localhost:3000',

  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },

  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID || '',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
    },
  },

  session: {
    expiresIn: 60 * 60 * 24 * 7,  // 7 ngày
    updateAge: 60 * 60 * 24,       // Refresh sau mỗi 1 ngày
  },

  user: {
    additionalFields: {
      avatarUrl: {
        type: 'string',
        required: false,
      },
    },
  },
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;
