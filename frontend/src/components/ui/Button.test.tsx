import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Button } from "./Button";

describe("Button", () => {
  it("renders label and respects loading state", () => {
    render(<Button isLoading>Sign in</Button>);
    expect(screen.getByRole("button")).toHaveTextContent("Loading...");
    expect(screen.getByRole("button")).toBeDisabled();
  });
});
