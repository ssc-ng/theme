# frozen_string_literal: true

require "jekyll"

# Brand layer for the SSC-NG sites. Jekyll allows one theme and has no theme
# inheritance, so this plugin runs alongside the real theme and adds its own
# folders to Jekyll's search paths.
module SscNgTheme
  ROOT = File.expand_path("..", __dir__)
  ASSET_DIR = "assets/ssc-ng-theme"
  LOGO = "/#{ASSET_DIR}/logo-400.png"

  def self.configure(site)
    add_sass_paths(site.config)
    # Position 1: after the site's own _includes, before the real theme's.
    site.includes_load_paths.insert(1, File.join(ROOT, "_includes"))

    theme = site.theme&.name
    case theme
    when "just-the-docs"
      # Replaces any local value, so that a site cannot drift from the brand.
      site.config["color_scheme"] = "ssc-ng"
      site.config["logo"] = LOGO
    else
      Jekyll.logger.warn "ssc-ng-theme:", "no brand layer for theme #{theme.inspect}"
    end
    nil
  end

  # User load paths precede the site's _sass, so list _sass first to keep the
  # site's own files ahead of the gem. The hash is mutated in place so that
  # other sass options survive.
  def self.add_sass_paths(config)
    sass = (config["sass"] ||= {})
    sass["load_paths"] = ["_sass", File.join(ROOT, "_sass"), *sass["load_paths"]]
  end
  private_class_method :add_sass_paths

  # Adds the logo and font files to the site's output.
  class AssetGenerator < Jekyll::Generator
    safe true

    def generate(site)
      Dir.children(File.join(ROOT, ASSET_DIR)).sort.each do |name|
        site.static_files << Jekyll::StaticFile.new(site, ROOT, ASSET_DIR, name)
      end
      nil
    end
  end
end

Jekyll::Hooks.register(:site, :after_init) { |site| SscNgTheme.configure(site) }
