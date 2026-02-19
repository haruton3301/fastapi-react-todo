import { QueryClient } from "@tanstack/react-query";
import {
  createRootRouteWithContext,
  Link,
  Outlet,
} from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { isLoggedIn, logout } from "../lib/auth";
import { useGetMeAuthMeGet } from "../api/generated";

export interface RouterContext {
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
});

function RootLayout() {
  const loggedIn = isLoggedIn();
  const { data: me } = useGetMeAuthMeGet({ query: { enabled: loggedIn } });

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-base-200">
      <header className="navbar px-4 bg-base-100 shadow-sm">
        <div className="flex-1">
          <Link to="/" className="btn btn-ghost text-xl">
            タスク管理
          </Link>
        </div>
        <div className="flex-none flex gap-2 items-center">
          {loggedIn ? (
            <>
              {me && <span className="text-sm mr-2">{me.username}</span>}
              <Link to="/statuses" className="btn btn-ghost btn-sm">
                ステータス管理
              </Link>
              <Link to="/tasks/new" className="btn btn-primary btn-sm">
                新規作成
              </Link>
              <button onClick={handleLogout} className="btn btn-ghost btn-sm">
                ログアウト
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost btn-sm">
                ログイン
              </Link>
              <Link to="/signup" className="btn btn-primary btn-sm">
                新規登録
              </Link>
            </>
          )}
        </div>
      </header>
      <main className="container mx-auto p-6">
        <Outlet />
      </main>
      <TanStackRouterDevtools />
    </div>
  );
}
