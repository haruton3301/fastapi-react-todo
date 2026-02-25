import { QueryClient } from "@tanstack/react-query";
import {
  createRootRouteWithContext,
  Link,
  Outlet,
} from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { logout, refreshAccessToken } from "../lib/auth";
import { useAuthStore } from "../store/auth";
import { getMeAuthMeGet } from "../api/generated";
import { FaUserCircle } from "react-icons/fa";

export interface RouterContext {
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  pendingComponent: () => (
    <div className="min-h-screen flex items-center justify-center">
      <span className="loading loading-spinner loading-lg" />
    </div>
  ),
  beforeLoad: async ({ cause }) => {
    if (cause !== "enter") return;
    try {
      await refreshAccessToken();
      const me = await getMeAuthMeGet();
      useAuthStore.getState().setUser(me);
    } catch {
      useAuthStore.getState().clearAuth();
    }
  },
  component: RootLayout,
});

function RootLayout() {
  const loggedIn = useAuthStore((s) => s.accessToken !== null);
  const username = useAuthStore((s) => s.user?.username);

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
              <Link to="/statuses" className="btn btn-ghost btn-sm">
                ステータス管理
              </Link>
              <Link to="/tasks/new" state={{ from: window.location.search }} className="btn btn-primary btn-sm">
                新規作成
              </Link>
              <div className="dropdown dropdown-end dropdown-hover">
                <div tabIndex={0} role="button" className="btn btn-ghost btn-sm gap-1">
                  <FaUserCircle className="text-lg" />
                  {username}
                </div>
                <ul tabIndex={0} className="dropdown-content menu bg-base-100 rounded-box shadow-sm w-40 p-2">
                  <li>
                    <Link to="/profile">プロフィール</Link>
                  </li>
                  <li>
                    <button onClick={handleLogout}>ログアウト</button>
                  </li>
                </ul>
              </div>
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
