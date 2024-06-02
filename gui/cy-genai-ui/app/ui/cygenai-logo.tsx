import { CubeTransparentIcon, GlobeAltIcon } from '@heroicons/react/24/outline';
import { lusitana } from './fonts';

export default function CyGenAILogo() {
  return (
    <div
      className={`${lusitana.className} flex flex-row items-center leading-none text-white`}
      >
      {/*<CubeTransparentIcon className="h-12 w-12 rotate-[15deg]" />*/}
      <p className="text-[26px]">Cy-GenAI</p>
    </div>
  );
}
