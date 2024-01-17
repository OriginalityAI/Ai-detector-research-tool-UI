import JSZip from 'jszip'
import type { TrueRates, zFolders } from '@/assets/types'

export const loadZip = async (blob: Blob) => {
  try {
    const zip = await new JSZip().loadAsync(blob)

    const zFolders: zFolders = {}

    // Iterate through each file
    for (const [relativePath, file] of Object.entries(zip.files)) {
      if (file.dir) continue

      // Extract folder name and file name
      const folderName = relativePath.split('/')[0]
      const fileName = relativePath.split('/').pop()

      // Initialize the folder object if it doesn't exist
      if (!zFolders[folderName]) {
        zFolders[folderName] = {
          name: folderName,
          trueRates: null,
          csv: null,
          txt: null,
          pngUrl: null
        }
      }

      // Assign the file content based on file type
      if (fileName!.endsWith('.csv')) {
        const csv = await file.async('text')
        zFolders[folderName].csv = csv
      } else if (fileName!.endsWith('.txt')) {
        const txt = await file.async('text')
        zFolders[folderName].txt = txt
        const trueRates = txt
          .trim()
          .split('\n')
          .map((s) => (([label, score]) => ({ label, score }))(s.split(':')))
          .reduce((acc: TrueRates, curr): TrueRates => ({ ...acc, [curr.label]: curr.score }), {})
        zFolders[folderName].trueRates = trueRates
      } else if (fileName!.endsWith('.png')) {
        const blob = await file.async('blob')
        const url = URL.createObjectURL(blob)
        zFolders[folderName].pngUrl = url
      }
    }
    // Convert the zFolders object to an array
    return Object.values(zFolders)
  } catch (err) {
    console.error(err)
  }
}
