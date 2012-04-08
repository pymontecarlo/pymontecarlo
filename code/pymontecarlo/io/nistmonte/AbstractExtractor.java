package pymontecarlo.io.nistmonte;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import org.jdom.Element;
import org.jdom.Namespace;

/**
 * Abstract implementation of the extractor interface.
 * 
 * @author ppinard
 */
public abstract class AbstractExtractor implements Extractor {

    /** XML namespace. */
    private final Namespace ns;

    /** XML tag. */
    private final Set<String> tags;



    /**
     * Creates a new <code>AbstractExtractor</code>.
     * 
     * @param tags
     *            required XML tag(s)
     */
    public AbstractExtractor(Namespace ns, String... tags) {
        this.ns = ns;
        this.tags = new HashSet<String>();
        this.tags.addAll(Arrays.asList(tags));
    }



    /**
     * Creates a new <code>AbstractExtractor</code>.
     * 
     * @param tags
     *            required XML tag(s)
     */
    public AbstractExtractor(String... tags) {
        this(Namespace.getNamespace("mc", "http://pymontecarlo.sf.net"), tags);
    }



    @Override
    public boolean canExtract(Element element) {
        if (element.getNamespace().equals(Namespace.NO_NAMESPACE))
            return tags.contains(element.getName());
        else
            return element.getNamespace().equals(ns)
                    && tags.contains(element.getName());
    }
}
