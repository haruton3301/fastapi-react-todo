import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { useAuthStore } from "../store/auth";

export const Route = createFileRoute("/_auth")({
  beforeLoad: () => {
    if (useAuthStore.getState().accessToken) {
      throw redirect({ to: "/" });
    }
  },
  component: () => <Outlet />,
});
