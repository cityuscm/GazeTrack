import { defineConfig, Preset, presetAttributify, presetIcons, presetWebFonts } from 'unocss';
import { presetWind4 } from '@unocss/preset-wind4';
import variantGroup from '@unocss/transformer-variant-group';
import { presetHeroPatterns } from '@julr/unocss-preset-heropatterns';

export default defineConfig({
	presets: [
		presetWind4({
			preflights: {
				reset: true
			}
		}),
		presetIcons(),
		presetWebFonts({
			provider: 'fontsource',
			fonts: {
				sans: 'Comfortaa'
			}
		}),
		presetAttributify(),
		presetHeroPatterns() as Preset
	],
	transformers: [variantGroup()],
	shortcuts: {
		'parent-size': 'absolute top-0 left-0 w-full h-full',
		'absolute-center': 'absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2'
	}
});
