import { RATE_LABELS } from "./global"

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

export type TrueRates = {
  [K in typeof RATE_LABELS[number]]?: string
}

export type Folder = {
  name: string
  trueRates: TrueRates | null
  csv: string | null
  txt: string | null
  pngUrl: string | null
}

export type zFolders = {
  [folderName: string]: Folder
}

export type MainResults = {
  folders: Folder[]
  blob: Blob | null 
}

export type OrderOptions = typeof RATE_LABELS

export type OrderSelect = {
  selected: typeof RATE_LABELS[number] | null | undefined
  options: OrderOptions 
  descending: boolean 
}

export type Pending = {
  status: boolean
  progress: string | null
  msg: string | null
}

export type PollResolve = {
  kind: string
  content: MainResults | OtherResult
}

export type OtherResult = {
  status: boolean
  msg: string | null
  blob: Blob | null
}