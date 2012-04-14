package pymontecarlo.program.nistmonte.io;

import java.util.List;

/**
 * Interface for all extrator factories.
 * 
 * @author ppinard
 * @param <T>
 *            type of extractor
 */
public interface ExtractorFactory<T> {

    /**
     * Returns a list of all model extractors.
     * 
     * @return list of all model extractors
     */
    public List<T> getAllExtractors();
}
