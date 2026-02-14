import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { isLoggedIn, removeToken } from "../lib/auth";
import {
  getMeAuthMeGet,
  getGetMeAuthMeGetQueryKey,
} from "../api/generated";

export const Route = createFileRoute("/_protected")({
  beforeLoad: async ({ context: { queryClient } }) => {
    if (!isLoggedIn()) {
      throw redirect({ to: "/login" });
    }
    try {
      await queryClient.ensureQueryData({
        queryKey: getGetMeAuthMeGetQueryKey(),
        queryFn: () => getMeAuthMeGet(),
      });
    } catch {
      removeToken();
      throw redirect({ to: "/login" });
    }
  },
  component: () => <Outlet />,
});
