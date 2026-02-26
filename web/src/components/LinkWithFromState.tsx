import { Link, type LinkComponentProps } from "@tanstack/react-router";

type Props = Omit<LinkComponentProps, "state">;

export function LinkWithFromState(props: Props) {
  return (
    <Link
      {...props}
      state={{ from: window.location.pathname + window.location.search }}
    />
  );
}
