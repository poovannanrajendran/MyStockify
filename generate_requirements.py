import pkg_resources

# Get a list of installed packages
installed_packages = pkg_resources.working_set
# Sort packages by name
sorted_packages = sorted(["{}=={}".format(i.key, i.version) for i in installed_packages])

# Write to requirements.txt without versions
with open("requirements.txt", "w") as f:
    for package in sorted_packages:
        # Remove version specification
        package_name = package.split("==")[0]
        f.write(f"{package_name}\n")
