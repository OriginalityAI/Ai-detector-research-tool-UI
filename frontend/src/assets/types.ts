export type UserInput = {
  csv: File | null;
  detectors: Detector;
}

export type Detector = {
  [detectorName: string]: {
    selected: boolean;
    key: string;
    additionalKey?: {
      name: string,
      value: string
    } | undefined;
  }
}
