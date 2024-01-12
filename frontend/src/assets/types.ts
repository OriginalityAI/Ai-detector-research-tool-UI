export type UserInput = {
  csv: File[] | undefined
  detectors: Detectors
}

export type Detectors = {
  [detectorName: string]: {
    selected: boolean
    key: string
    additionalKey?:
      | {
          name: string
          value: string
        }
      | undefined
  }
}

export type DetectorItem = {
  name: string
  selected: boolean;
  key: string;
  additionalKey?: {
    name: string,
    value: string
  } | undefined;
}