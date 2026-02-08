import { createFileRoute } from "@tanstack/react-router";
import { TaskList } from "../components/task/TaskList";

export const Route = createFileRoute("/")({
  component: Index,
});

function Index() {
  return <TaskList />;
}
