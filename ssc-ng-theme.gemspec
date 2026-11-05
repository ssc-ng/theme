Gem::Specification.new do |spec|
  spec.name = "ssc-ng-theme"
  spec.version = "1.3.0"
  spec.summary = "Shared look for the SSC-NG websites"
  spec.authors = ["SSC Next Generation"]
  spec.license = "MIT"
  spec.homepage = "https://github.com/ssc-ng/theme"
  spec.required_ruby_version = ">= 3.3"
  spec.files = Dir["lib/**/*", "_includes/**/*", "_sass/**/*", "assets/**/*", "LICENSE"]
  spec.add_dependency "jekyll", ">= 4.3", "< 5"
end
