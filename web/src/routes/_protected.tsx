import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { useAuthStore } from "../store/auth";

export const Route = createFileRoute("/_protected")({
  beforeLoad: () => {
    if (!useAuthStore.getState().user) {
      throw redirect({ to: "/login" });
    }
  },
  component: () => <Outlet />,
});
