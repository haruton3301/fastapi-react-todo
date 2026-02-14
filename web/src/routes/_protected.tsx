import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { isLoggedIn } from "../lib/auth";

export const Route = createFileRoute("/_protected")({
  beforeLoad: () => {
    if (!isLoggedIn()) {
      throw redirect({ to: "/login" });
    }
  },
  component: () => <Outlet />,
});
