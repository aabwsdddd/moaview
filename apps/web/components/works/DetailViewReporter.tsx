"use client";

import { useEffect } from "react";
import { recordDetailViewEvent } from "../../lib/api";

export function DetailViewReporter({ workId }: { workId: string }) {
  useEffect(() => {
    void recordDetailViewEvent(workId);
  }, [workId]);

  return null;
}
