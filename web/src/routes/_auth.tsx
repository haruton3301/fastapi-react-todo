import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { isLoggedIn } from "../lib/auth";

export const Route = createFileRoute("/_auth")({
  beforeLoad: () => {
    if (isLoggedIn()) {
      throw redirect({ to: "/" });
    }
  },
  component: () => <Outlet />,
});
