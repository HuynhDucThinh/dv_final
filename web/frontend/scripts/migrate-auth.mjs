/**
 * Script chạy Better Auth database migration
 * Tạo các bảng: user, account, session, verification
 *
 * Chạy: node scripts/migrate-auth.mjs
 * (Cần đã điền DATABASE_URL trong .env)
 */
import { betterAuth } from 'better-auth';
import { Pool } from 'pg';
import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Load .env thủ công
const envPath = resolve(__dirname, '../../.env');
try {
  const envContent = readFileSync(envPath, 'utf-8');
  for (const line of envContent.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const [key, ...valueParts] = trimmed.split('=');
    if (key && valueParts.length > 0) {
      process.env[key.trim()] = valueParts.join('=').trim();
    }
  }
  console.log('✅ Loaded .env from', envPath);
} catch {
  console.warn('⚠️  Could not load .env, relying on system environment variables.');
}

const DATABASE_URL = process.env.DATABASE_URL;
if (!DATABASE_URL || DATABASE_URL.includes('YOUR_PASSWORD')) {
  console.error('❌ DATABASE_URL is not configured. Please update .env with your Supabase connection string.');
  process.exit(1);
}

const pool = new Pool({ connectionString: DATABASE_URL });

const auth = betterAuth({
  database: { db: pool, type: 'pg' },
  secret: process.env.BETTER_AUTH_SECRET || 'migration-secret',
  emailAndPassword: { enabled: true },
  socialProviders: {
    google: { clientId: 'placeholder', clientSecret: 'placeholder' },
  },
});

console.log('🔄 Running Better Auth database migration...');

try {
  // Better Auth có built-in migrate method
  // @ts-ignore
  await auth.db.migrate();
  console.log('✅ Better Auth migration completed!');
  console.log('   Tables created: user, account, session, verification');
} catch (err) {
  console.error('❌ Migration failed:', err.message);
  console.log('\n💡 Alternative: Run the SQL manually in Supabase SQL Editor:');
  console.log('   npx better-auth generate --output ./scripts/auth-schema.sql');
} finally {
  await pool.end();
}
