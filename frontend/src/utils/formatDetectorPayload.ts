import type { UserInput } from "@/assets/types";

type DetectorPayload = {
  [detectorName: string]: [boolean, string]
}

export const formatDetectorPayload = (input: UserInput): DetectorPayload => {
  return Object.entries(input.detectors).reduce((acc: DetectorPayload, [name, data]): DetectorPayload => {
    const jsonKey = `${name.toUpperCase()}_API_KEY`
    acc[jsonKey] = [data.selected, data.key]
    if (data.additionalKey) {
      const jsonAddKey = `${name.toUpperCase()}_${data.additionalKey.name.toUpperCase().split(' ').join('_')}` // names used for additional authentication by different services are not consistent
      acc[jsonAddKey] = [data.selected, data.additionalKey.value]
    }
    return acc;
  }, {});
}