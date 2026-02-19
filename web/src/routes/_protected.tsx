import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { isLoggedIn } from "../lib/auth";
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
        staleTime: 1000 * 60 * 5,
      });
    } catch {
      throw redirect({ to: "/login" });
    }
  },
  component: () => <Outlet />,
});
