_dephell()
{
  local first second current double
  COMPREPLY=()
  first="${COMP_WORDS[1]}"
  second="${COMP_WORDS[2]}"
  double="${COMP_WORDS[1]} ${COMP_WORDS[2]}"
  current="${COMP_WORDS[COMP_CWORD]}"

  # autocomplete command first word
  if [[ ${first} == ${current} ]] ; then
    COMPREPLY=( $(compgen -W "jail generate autocomplete venv install inspect deps build --help" -- ${current}) )
    return 0
  fi

  # autocomplete command second word
  if [[ ${second} == ${current} ]] ; then
    case "${first}" in
      
        deps)
          COMPREPLY=( $(compgen -W "convert install licenses " -- ${current}) )
          return 0
          ;;
      
        generate)
          COMPREPLY=( $(compgen -W "license editorconfig authors config " -- ${current}) )
          return 0
          ;;
      
        inspect)
          COMPREPLY=( $(compgen -W "venv config " -- ${current}) )
          return 0
          ;;
      
        jail)
          COMPREPLY=( $(compgen -W "install remove " -- ${current}) )
          return 0
          ;;
      
        venv)
          COMPREPLY=( $(compgen -W "destroy run create shell " -- ${current}) )
          return 0
          ;;
      
      *)
      ;;
    esac
  fi

  # autocomplete one-word command arguments
  case "${first}" in
    
      "autocomplete")
        COMPREPLY=( $(compgen -W "--env --config --nocolors -h -c --format --silent --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "build")
        COMPREPLY=( $(compgen -W "--warehouse --help --from-format --bitbucket -e --level --env --config --cache-ttl --nocolors -h -c --silent --cache-path --traceback --from --envs --prereleases --from-path --strategy --format --project --bin " -- ${current}) )
        return 0
        ;;
    
      "deps convert")
        COMPREPLY=( $(compgen -W "--warehouse --to --help --from-format --bitbucket --to-path -e --level --env --to-format --config --cache-ttl --nocolors -h -c --silent --cache-path --traceback --from --envs --prereleases --from-path --strategy --format --project --bin " -- ${current}) )
        return 0
        ;;
    
      "deps install")
        COMPREPLY=( $(compgen -W "--warehouse --help --from-format --bitbucket -e --level --env --config --cache-ttl --nocolors -h -c --silent --venv --cache-path --traceback --from --envs --prereleases --from-path --strategy --format --project --python --bin " -- ${current}) )
        return 0
        ;;
    
      "deps licenses")
        COMPREPLY=( $(compgen -W "--warehouse --help --from-format --bitbucket -e --level --env --config --cache-ttl --nocolors -h -c --silent --cache-path --traceback --from --envs --prereleases --from-path --strategy --format --project --bin " -- ${current}) )
        return 0
        ;;
    
      "generate authors")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "generate config")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "generate editorconfig")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "generate license")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "inspect config")
        COMPREPLY=( $(compgen -W "--warehouse --to --help --from-format --bitbucket --to-path -e --level --env --to-format --config --cache-ttl --nocolors -h -c --silent --venv --cache-path --traceback --from --envs --prereleases --from-path --strategy --format --project --python --bin " -- ${current}) )
        return 0
        ;;
    
      "inspect venv")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --python --venv --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "install")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --python --venv --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "jail install")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --python --venv --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "jail remove")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --python --venv --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "venv create")
        COMPREPLY=( $(compgen -W "--help --from-format -e --level --env --config --cache-ttl --nocolors -h -c --silent --venv --cache-path --traceback --from --envs --from-path --project --format --python --bin " -- ${current}) )
        return 0
        ;;
    
      "venv destroy")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "venv run")
        COMPREPLY=( $(compgen -W "--warehouse --help --bitbucket -e --level --env --config --cache-ttl --nocolors -h -c --silent --venv --cache-path --traceback --envs --project --format --python --bin " -- ${current}) )
        return 0
        ;;
    
      "venv shell")
        COMPREPLY=( $(compgen -W "--help --from-format -e --level --env --config --cache-ttl --nocolors -h -c --silent --venv --cache-path --traceback --from --envs --from-path --project --format --python --bin " -- ${current}) )
        return 0
        ;;
    
    *)
    ;;
  esac

  # autocomplete two-words command arguments
  case "${double}" in
    
      "autocomplete")
        COMPREPLY=( $(compgen -W "--env --config --nocolors -h -c --format --silent --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "build")
        COMPREPLY=( $(compgen -W "--warehouse --help --from-format --bitbucket -e --level --env --config --cache-ttl --nocolors -h -c --silent --cache-path --traceback --from --envs --prereleases --from-path --strategy --format --project --bin " -- ${current}) )
        return 0
        ;;
    
      "deps convert")
        COMPREPLY=( $(compgen -W "--warehouse --to --help --from-format --bitbucket --to-path -e --level --env --to-format --config --cache-ttl --nocolors -h -c --silent --cache-path --traceback --from --envs --prereleases --from-path --strategy --format --project --bin " -- ${current}) )
        return 0
        ;;
    
      "deps install")
        COMPREPLY=( $(compgen -W "--warehouse --help --from-format --bitbucket -e --level --env --config --cache-ttl --nocolors -h -c --silent --venv --cache-path --traceback --from --envs --prereleases --from-path --strategy --format --project --python --bin " -- ${current}) )
        return 0
        ;;
    
      "deps licenses")
        COMPREPLY=( $(compgen -W "--warehouse --help --from-format --bitbucket -e --level --env --config --cache-ttl --nocolors -h -c --silent --cache-path --traceback --from --envs --prereleases --from-path --strategy --format --project --bin " -- ${current}) )
        return 0
        ;;
    
      "generate authors")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "generate config")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "generate editorconfig")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "generate license")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "inspect config")
        COMPREPLY=( $(compgen -W "--warehouse --to --help --from-format --bitbucket --to-path -e --level --env --to-format --config --cache-ttl --nocolors -h -c --silent --venv --cache-path --traceback --from --envs --prereleases --from-path --strategy --format --project --python --bin " -- ${current}) )
        return 0
        ;;
    
      "inspect venv")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --python --venv --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "install")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --python --venv --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "jail install")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --python --venv --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "jail remove")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --python --venv --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "venv create")
        COMPREPLY=( $(compgen -W "--help --from-format -e --level --env --config --cache-ttl --nocolors -h -c --silent --venv --cache-path --traceback --from --envs --from-path --project --format --python --bin " -- ${current}) )
        return 0
        ;;
    
      "venv destroy")
        COMPREPLY=( $(compgen -W "--env --config --cache-ttl --envs --nocolors -h -c --project --format --silent --bin --cache-path --help --traceback -e --level " -- ${current}) )
        return 0
        ;;
    
      "venv run")
        COMPREPLY=( $(compgen -W "--warehouse --help --bitbucket -e --level --env --config --cache-ttl --nocolors -h -c --silent --venv --cache-path --traceback --envs --project --format --python --bin " -- ${current}) )
        return 0
        ;;
    
      "venv shell")
        COMPREPLY=( $(compgen -W "--help --from-format -e --level --env --config --cache-ttl --nocolors -h -c --silent --venv --cache-path --traceback --from --envs --from-path --project --format --python --bin " -- ${current}) )
        return 0
        ;;
    
    *)
    ;;
  esac
}
complete -F _dephell dephell
