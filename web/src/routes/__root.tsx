import { createRootRoute, Link, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  return (
    <div className="min-h-screen bg-base-200">
      <header className="navbar px-4 bg-base-100 shadow-sm">
        <div className="flex-1">
          <Link to="/" className="btn btn-ghost text-xl">
            タスク管理
          </Link>
        </div>
        <div className="flex-none flex gap-2">
          <Link to="/statuses" className="btn btn-ghost btn-sm">
            ステータス管理
          </Link>
          <Link to="/tasks/new" className="btn btn-primary btn-sm">
            新規作成
          </Link>
        </div>
      </header>
      <main className="container mx-auto p-6">
        <Outlet />
      </main>
      <TanStackRouterDevtools />
    </div>
  );
}
