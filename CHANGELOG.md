# Changelog

## [0.3.0](https://github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/compare/v0.2.2...v0.3.0) (2026-10-20)


### Features

* bump multiqc to 1.27.1 ([610e7ac](https://github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/610e7ac23891b0568966f2739f89622d874cbcfc))
* bump multiqc to 1.27.1 ([610e7ac](https://github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/610e7ac23891b0568966f2739f89622d874cbcfc))
* bump multiqc to 1.27.1 ([5b6c7e2](https://github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/5b6c7e2efa767f876e9a109c5b4b27d75520ac09))


### Bug Fixes

* there is no lane 0 ([e6474ce](https://github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/e6474ce25ae29e6985b11eaf8c0a48e39d33409c))

### [0.2.2](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/compare/v0.2.1...v0.2.2) (2024-08-23)


### Bug Fixes

* if missing PanelMedian set to NA and do not break ([4da94af](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/4da94af11390cfb1f397ca452937403c3a6d36b5))

### [0.2.1](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/compare/v0.2.0...v0.2.1) (2024-06-04)


### Bug Fixes

* update multiqc filename to match new stackstorm ([b5a9d21](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/b5a9d21dfc280ac0a8f8a9a7feb93c360ceac4e2))

## [0.2.0](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/compare/v0.1.0...v0.2.0) (2024-04-24)


### Features

* add background annotation to vcf ([688b797](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/688b79752066e5584aaa1976c22820c5c94f7243))
* add background annotation to xlsx ([c8ef16a](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/c8ef16ad5704071666da1d98ff03e434ddd73c38))
* add background creation in seperate snakefile ([58018c0](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/58018c09af775214b277ca29446b7eb5ce53cc50))
* add background levels to vcf and xlsx report ([9359b21](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/9359b2160bab496b6890973cca80fc39fca578ef))
* add varible function to config (PATH_TO_REPO) ([e7ed2a9](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/e7ed2a9703cd4f4743e0dee69cee5e8546a8ebc8))
* change pisces to genome vcf and add reference module to create background file ([6b9d5f6](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/6b9d5f6a819465837eb7c0c6251d769202988a7e))
* remove use of SampleSheet, instead base multiqc-order on S-index ([a6415d2](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/a6415d21c68ad8bb6f345864f30b27f9b47f2d21))


### Bug Fixes

* fix pulp version to < 2.8 ([9a70ac7](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/9a70ac7c6d57cc26a16fe241beb1a3e357a6a856))
* lock smart_open to <7.0.0 ([2adfec1](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/2adfec185044e7afa72e01ba37426d5efb7353bd))
* path to fastp for multiqc updated ([5a97c2d](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/5a97c2db9262ce1b5cb8e18aceb8dcd9d68c1bef))
* remove unused ruleorder and small style changes ([3202054](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/3202054cfc9b3bb6ffe251bc5e7815784d13c6b3))
* update output files to remove log and benchmark files in Results ([7d1803c](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/7d1803c00e805270b05c5f6d0e9e466382a6cecd))


### Documentation

* fix dead link and output message in rule ([1ac9fdb](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/1ac9fdb4b46bb9860c10fbe081a5ae7f8147dfda))
* update readme ([a5aafb0](https://www.github.com/clinical-genomics-uppsala/pickett_bcr_abl_pipeline/commit/a5aafb0665cef0905c161a76cfc82b41b35e681f))

## 0.1.0 (2023-03-27)


### Features

* add E292K to branford list ([f4baf61](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/f4baf618d3a469c38779a34776522de709902e0c))
* add rseqc inner dist and gene body cov to multiqc ([a109fb3](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/a109fb3e1ba88ae5d4c68a50b9c6bcac5cc210ec))
* add sample order button in multiqc based on samplesheet ([f11d5de](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/f11d5de7ed00f0782cbf0612da2e8542c16d9eae))
* add samtools stats and style fix for multiqc general stats ([80706e7](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/80706e7ec4a503d80474c36762a38e8c9a5c6c3b))
* add xlsx report for branford list and other snvs ([a650243](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/a65024347a31ef8551896ba4ba3fa0ae65f350d7))
* added arriba fusion calls to xlsx-file ([50f81ba](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/50f81babb89a4df7870027471542f243acd70b0f))
* change mutect2 to pisces inital commit ([dee06af](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/dee06af13cc31b1db35c5aa0793a3fb02e37bf0b))
* pipeline until vcf ([494afe8](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/494afe88887bae04a8df0fa6a01b26592b90a7f7))
* update multiqc general stats table ([7171b2e](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/7171b2eae9e57df1fa4ff394d50c57f592602973))


### Bug Fixes

* correct path to pisces files ([72e3833](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/72e38334f6adc1865c2c591a5c1bd3a52838611e))
* fix duplicated lines in branfordlist and put hits on top ([d9586e8](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/d9586e80eaa8ad0010aa9b2ab37c4b9a2b2e455f))
* fix duplicated lines in branfordlist and put hits on top ([6534e03](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/6534e03e0a1286b0a6b1e7ed1dd539629ca522e0))
* fix output for type r ([b49841e](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/b49841e9d812f3d957d5da228e1414f162e1482b))
* keep haplotype variants when hardfiltering ([28df91e](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/28df91eb77780f00e1f15efcddc4094807db62f9))
* spelling in test config ([492eaea](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/492eaea198354238cc928064e70f5b6cd3f04fa5))


### Documentation

* add rulegraph ([8eacf40](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/8eacf40b76154345595e808f2ffbc983cf06b2cb))
* remove hardcoded paths in example config ([e911d51](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/e911d51c9d89ad0d0086b67a68f2cf155c89d5f4))
* rulegraph update ([9c3eade](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/9c3eade23dfb8a16705ee3465c2851b5800dcb39))
* update rulegraph ([87035b9](https://www.github.com/clinical-genomics-uppsala/bcr_abl_pipeline/commit/87035b92d6d916d93050888a3dabb1bd25ff759d))
