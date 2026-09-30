# trprint

Custom Traceback printer

**No Dependencies**

## Install

```bash
pip install trprint
```

## Usage

```python
>>> from trprint import tprint
>>> try:
       print(sys.argv[1])
    except:
       tprint()
       
>>> # output with colors:
 2026-09-30 20:08:52.888009 - <class 'IndexError'> : list index out of range
    File "<ipython-input-4-05d459f38238>", line 2, in <module>
      print(sys.argv[1])
            ~~~~~~~~^^^

 2026-09-30 20:08:52.888009 - <class 'IndexError'> : list index out of range

```

[![Screenshot](https://raw.githubusercontent.com/cumulus13/trprint/master/screenshot.png)](https://raw.githubusercontent.com/cumulus13/trprint/master/screenshot.png)


## 👤 Author
        
[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    
[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)
 
[Support me on Patreon](https://www.patreon.com/cumulus13)